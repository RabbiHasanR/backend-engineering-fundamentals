# gRPC Production-Ready Best Practices Guide

> Everything you need to build stable, scalable, high-traffic gRPC microservices.
> Written in plain English with real examples.

---

## Table of Contents

1. [Channel and Connection Management](#1-channel-and-connection-management)
2. [Load Balancing in Kubernetes](#2-load-balancing-in-kubernetes)
3. [Keepalive — Prevent Silent TCP Drops](#3-keepalive--prevent-silent-tcp-drops)
4. [Concurrency — Sync vs Async](#4-concurrency--sync-vs-async)
5. [Deadlines — Set on Every RPC](#5-deadlines--set-on-every-rpc)
6. [Retry Policy — Configure Carefully](#6-retry-policy--configure-carefully)
7. [Rate Limiting and Throttling](#7-rate-limiting-and-throttling)
8. [Circuit Breaking](#8-circuit-breaking)
9. [Interceptors — Your Middleware Layer](#9-interceptors--your-middleware-layer)
10. [Security — TLS, mTLS, Auth](#10-security--tls-mtls-auth)
11. [Authorization](#11-authorization)
12. [Error Handling — Use the Right Status Codes](#12-error-handling--use-the-right-status-codes)
13. [Rich Error Model](#13-rich-error-model)
14. [Payload Optimization](#14-payload-optimization)
15. [Flow Control and Backpressure](#15-flow-control-and-backpressure)
16. [Streaming Best Practices](#16-streaming-best-practices)
17. [Health Checks](#17-health-checks)
18. [Observability — Metrics, Tracing, Logging](#18-observability--metrics-tracing-logging)
19. [Graceful Shutdown](#19-graceful-shutdown)
20. [Production Checklist](#20-production-checklist)

---

## 1. Channel and Connection Management

### Rule: One channel per service, reused forever

A channel is a real TCP connection. Creating one per request means a DNS lookup, TCP handshake, and HTTP/2 handshake on every call. Under load this adds 50–200ms per request and exhausts file descriptors fast.

```python
# WRONG — new TCP connection on every request
def get_user(user_id):
    channel = grpc.insecure_channel('userservice:50051')  # new TCP every time
    stub = UserServiceStub(channel)
    return stub.GetUser(UserRequest(id=user_id))

# CORRECT — create once at startup, reuse for all requests
channel = grpc.insecure_channel('userservice:50051', options=[...])
stub = UserServiceStub(channel)

def get_user(user_id):
    return stub.GetUser(UserRequest(id=user_id))  # reuses TCP, new HTTP/2 stream only
```

### Rule: Use a channel pool for very high concurrency

A single HTTP/2 connection supports up to 100 concurrent streams by default (often set by Envoy). If you have hundreds of goroutines or threads all hitting one service simultaneously, one channel becomes a bottleneck. Use a pool.

```python
import random

# Create a pool of channels to the same service
POOL_SIZE = 5
channel_pool = [
    grpc.insecure_channel('userservice:50051', options=[
        ('grpc.channel_args_unique_id', i)  # different args = separate TCP connections
    ])
    for i in range(POOL_SIZE)
]

def get_stub():
    # pick a random channel from the pool
    return UserServiceStub(random.choice(channel_pool))
```

> **Why this works:** Each channel in the pool is a separate TCP connection with its own set of 100 HTTP/2 streams. A pool of 5 channels = 500 concurrent RPCs without queuing.
>
> This is a temporary workaround. The gRPC team is working on a built-in fix for connection concurrency limits.

### Set message size limits

```python
server = grpc.server(executor, options=[
    ('grpc.max_receive_message_length', 4 * 1024 * 1024),  # 4MB max incoming
    ('grpc.max_send_message_length',    4 * 1024 * 1024),  # 4MB max outgoing
    ('grpc.max_concurrent_rpcs', 200),                      # queue beyond this
])
```

Never raise the limit to 100MB just to handle large files. Use streaming or object storage (S3) instead. A 100MB payload under load = 100MB RAM allocated per request = OOM crash.

---

## 2. Load Balancing in Kubernetes

### The biggest gRPC mistake in Kubernetes — using ClusterIP

By default, Kubernetes creates a ClusterIP Service. For REST (HTTP/1.1) this is fine — every request opens a new TCP connection, so kube-proxy load-balances each one across pods. For gRPC this silently breaks.

```
REST + ClusterIP (works fine):
  Client → new TCP per request → ClusterIP → kube-proxy → random pod each time ✓

gRPC + ClusterIP (broken):
  Client → 1 persistent TCP → ClusterIP → kube-proxy → always pod A
  Pod B, C, D are idle. Pod A is overloaded.
```

gRPC reuses TCP connections. Once the connection is established to pod A, all RPCs go there forever. Other pods receive nothing.

### Solution A — Headless Service (recommended for client-side LB)

```yaml
# kubernetes service
apiVersion: v1
kind: Service
metadata:
  name: userservice
spec:
  clusterIP: None      # headless — DNS returns all pod IPs directly
  selector:
    app: userservice
  ports:
    - port: 50051
```

```python
# gRPC client — use dns:/// prefix and round_robin
import json

service_config = json.dumps({
    'loadBalancingConfig': [{'round_robin': {}}]
})

channel = grpc.insecure_channel(
    'dns:///userservice.default.svc.cluster.local:50051',
    options=[('grpc.service_config', service_config)]
)
```

Now DNS returns `[pod-A-IP, pod-B-IP, pod-C-IP]`. gRPC creates one subchannel (TCP) per pod and round-robins RPCs across all three.

### Solution B — Service Mesh (Envoy / Istio / Linkerd)

The easiest option operationally. Install Istio/Linkerd. The sidecar proxy intercepts all traffic, understands HTTP/2 frames, and balances individual RPCs across pods. No code changes needed.

```
Client app → sidecar (localhost) → Istio control plane → pod A / B / C
                                    (HTTP/2-aware, per-RPC LB)
```

### Solution C — L7 Load Balancer (AWS ALB / nginx)

AWS ALB with gRPC support terminates HTTP/2 and re-initiates it to backends. This means it CAN load balance per-RPC. Add latency (one extra network hop) but no service mesh complexity.

### L4 vs L7 — Why it matters

| Type | Example | Understands HTTP/2? | gRPC LB works? |
|---|---|---|---|
| L4 (TCP) | AWS NLB | No | No — pins connection to 1 pod |
| L7 (HTTP) | AWS ALB, Envoy | Yes | Yes — balances per RPC |
| Service mesh | Istio, Linkerd | Yes | Yes — per RPC, no code change |
| Client-side | round_robin + headless | Yes | Yes — most efficient |

> **Rule:** Never use raw ClusterIP for gRPC in production. Use headless service + `round_robin`, a service mesh, or an L7 load balancer.

---

## 3. Keepalive — Prevent Silent TCP Drops

### What happens without keepalive

Firewalls, AWS NAT gateways, GCP load balancers, and cloud proxies silently drop idle TCP connections after 1–10 minutes. They do not send a FIN or RST packet. The gRPC client still sees the subchannel as `READY`. The next RPC goes into a black hole and hangs until the OS TCP timeout fires — which can take several minutes.

This is the most common production mystery: "RPCs work fine under load but randomly hang during quiet periods."

### Configure keepalive on the client

```python
channel = grpc.insecure_channel('userservice:50051', options=[
    # Send a keepalive ping every 10 seconds when the connection is idle
    ('grpc.keepalive_time_ms', 10000),

    # If no ack received within 5 seconds, close and reconnect
    ('grpc.keepalive_timeout_ms', 5000),

    # Send pings even when there are no active RPCs
    ('grpc.keepalive_permit_without_calls', True),

    # Allow unlimited pings without data frames
    ('grpc.http2.max_pings_without_data', 0),
])
```

### Configure keepalive on the server

The server must accept client pings or it will terminate the connection for "too many pings" (a default self-protection mechanism).

```python
server = grpc.server(executor, options=[
    # Accept pings no faster than every 5 seconds
    ('grpc.keepalive_min_time_ms', 5000),

    # Allow pings even when there are no active streams
    ('grpc.http2.min_ping_interval_without_data_ms', 5000),
])
```

> **Rule:** Always configure keepalive on both client AND server. Configuring only the client will cause the server to drop the connection for "ping flooding."

---

## 4. Concurrency — Sync vs Async

### Python: sync gRPC will choke under load

The default Python gRPC server uses `ThreadPoolExecutor`. Each RPC occupies a thread. The Python GIL (Global Interpreter Lock) prevents true parallelism. Under high traffic you will hit thread starvation quickly.

```python
# SYNC — limited by thread count and GIL
server = grpc.server(
    futures.ThreadPoolExecutor(max_workers=10)  # only 10 concurrent RPCs!
)
```

### Python: use grpc.aio for high traffic

`grpc.aio` uses asyncio. A single thread handles thousands of concurrent I/O-bound RPCs. The bottleneck shifts from threads to actual CPU work.

```python
import grpc.aio
import asyncio

class UserServicer(UserServiceServicer):
    async def GetUser(self, request, context):
        # async DB call — does not block the thread
        user = await db.get_user(request.id)
        return UserResponse(id=user.id, name=user.name)

async def serve():
    server = grpc.aio.server()
    add_UserServiceServicer_to_server(UserServicer(), server)
    server.add_insecure_port('[::]:50051')
    await server.start()
    await server.wait_for_termination()

asyncio.run(serve())
```

> **Rule for Python:** Use `grpc.aio` for any service handling more than a few hundred RPCs per second. Sync gRPC in Python is only suitable for low-QPS internal tools.
>
> Also avoid the `future` API in sync Python gRPC — it creates an extra thread per call, making things worse.

### Avoid streaming in Python unless necessary

In Python, streaming RPCs create extra threads for send/receive, making them significantly slower than unary RPCs. Unlike Go or Java where streaming is efficient, in Python prefer unary calls unless streaming gives a major simplicity benefit.

---

## 5. Deadlines — Set on Every RPC

### Why deadlines matter

Without a deadline, a single slow or crashed downstream service can hold your thread forever. In a chain of microservices, one slow service hangs everything above it. Under load this cascades into a full system freeze within seconds.

```python
# WRONG — no deadline, will hang if server is slow or dead
response = stub.GetUser(UserRequest(id=42))

# CORRECT — always set a deadline
response = stub.GetUser(UserRequest(id=42), timeout=2.0)  # 2 seconds max
```

### Set default deadlines in service config

```python
service_config = json.dumps({
    'methodConfig': [{
        'name': [{'service': 'UserService'}],
        'timeout': '2s'    # default for all methods in this service
    }, {
        'name': [{'service': 'ReportService', 'method': 'GenerateReport'}],
        'timeout': '30s'   # specific method override
    }]
})
```

### Propagate deadlines across service chains

This is critical. If Service A has a 5s deadline and takes 0.5s of its own work, it should pass the remaining ~4.5s to Service B. If it does not, Service B will use its own default deadline (say 10s) and keep working long after the client gave up.

```python
def GetOrder(self, request, context):
    remaining = context.time_remaining()

    # If less than 50ms left, not worth calling downstream
    if remaining < 0.05:
        context.abort(grpc.StatusCode.DEADLINE_EXCEEDED, 'not enough time left')
        return

    # Pass remaining time minus 20% buffer to downstream
    user = user_stub.GetUser(
        UserRequest(id=request.user_id),
        timeout=remaining * 0.8
    )
    return build_order_response(request, user)
```

```
Without propagation:
  Client deadline: 2s → expires → client gives up
  Service B: still running query (10s default) — wasting resources

With propagation:
  Client deadline: 2s → Service A passes 1.8s to B → B passes 1.4s to C
  All services stop at the same time → no wasted work anywhere
```

---

## 6. Retry Policy — Configure Carefully

### Configure retry in service config, not in business logic

```python
service_config = json.dumps({
    'methodConfig': [{
        # Only retry idempotent read operations
        'name': [{'service': 'UserService', 'method': 'GetUser'}],
        'retryPolicy': {
            'maxAttempts': 3,
            'initialBackoff': '0.1s',
            'maxBackoff': '1s',
            'backoffMultiplier': 2,
            'retryableStatusCodes': ['UNAVAILABLE']
        }
    }, {
        # NO retry for writes — duplicate creates are dangerous
        'name': [{'service': 'OrderService', 'method': 'CreateOrder'}],
        # no retryPolicy here
    }]
})
```

### Which status codes are safe to retry?

| Status code | Retry? | Why |
|---|---|---|
| `UNAVAILABLE` | Yes | Server temporarily down, pod restarting |
| `DEADLINE_EXCEEDED` | Only if idempotent | Retrying a timeout under load makes things worse |
| `RESOURCE_EXHAUSTED` | No | Server is already overloaded — retrying makes it worse |
| `INVALID_ARGUMENT` | No | Bad data — retrying will fail again |
| `NOT_FOUND` | No | Resource doesn't exist |
| `INTERNAL` | No | Server bug — fix the code, not retry |
| `UNAUTHENTICATED` | No | Refresh token first, then retry manually |

### Deadline always beats retry

```
Deadline = 2s, maxAttempts = 3, backoff = 0.1s + 0.2s

attempt 1 → takes 0.9s → UNAVAILABLE → wait 0.1s  (total: 1.0s)
attempt 2 → takes 0.9s → UNAVAILABLE → wait 0.2s  (total: 2.1s) ← deadline hits here
attempt 3 never runs → DEADLINE_EXCEEDED returned to caller
```

Set your deadline long enough to allow all retry attempts to complete.

### Prevent retry storms

If 10% of RPCs fail and each retries 3 times, your downstream gets 30% extra load when it is already struggling. Prevent this:

- Keep `maxAttempts` at 2 or 3, never higher
- Always use exponential backoff with jitter
- Never retry `RESOURCE_EXHAUSTED` — the server is telling you to back off

---

## 7. Rate Limiting and Throttling

Rate limiting protects your server from being overwhelmed. It runs as a server-side interceptor so it applies to every RPC automatically.

### Token bucket rate limiter (per-server global limit)

```python
import time
import threading

class TokenBucket:
    """Allows `rate` requests per second with a burst of `burst`."""
    def __init__(self, rate, burst):
        self.rate = rate          # tokens added per second
        self.burst = burst        # max tokens (burst capacity)
        self.tokens = burst       # start full
        self.last_refill = time.monotonic()
        self.lock = threading.Lock()

    def allow(self):
        with self.lock:
            now = time.monotonic()
            elapsed = now - self.last_refill
            # Add tokens for elapsed time
            self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
            self.last_refill = now

            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False  # no tokens left — reject


class RateLimitInterceptor(grpc.ServerInterceptor):
    def __init__(self, rate_per_second=1000, burst=100):
        self.limiter = TokenBucket(rate=rate_per_second, burst=burst)

    def intercept_service(self, continuation, handler_call_details):
        def wrapper(request, context):
            if not self.limiter.allow():
                context.abort(
                    grpc.StatusCode.RESOURCE_EXHAUSTED,
                    'rate limit exceeded — try again later'
                )
                return
            return continuation(handler_call_details)(request, context)

        return grpc.unary_unary_rpc_method_handler(wrapper)


# Attach to server
server = grpc.server(
    executor,
    interceptors=[RateLimitInterceptor(rate_per_second=1000, burst=200)]
)
```

### Per-client rate limiting (throttling per caller)

Different clients get different limits. A free-tier client gets 100 RPS, a paid client gets 5000 RPS.

```python
from collections import defaultdict

class PerClientRateLimiter(grpc.ServerInterceptor):
    def __init__(self):
        self.limiters = defaultdict(lambda: TokenBucket(rate=100, burst=20))
        self.lock = threading.Lock()

    def get_client_id(self, context):
        # Extract from metadata — set by client auth interceptor
        metadata = dict(context.invocation_metadata())
        return metadata.get('x-client-id', context.peer())  # fallback to IP

    def intercept_service(self, continuation, handler_call_details):
        def wrapper(request, context):
            client_id = self.get_client_id(context)

            with self.lock:
                limiter = self.limiters[client_id]

            if not limiter.allow():
                context.abort(
                    grpc.StatusCode.RESOURCE_EXHAUSTED,
                    f'rate limit exceeded for client {client_id}'
                )
                return
            return continuation(handler_call_details)(request, context)

        return grpc.unary_unary_rpc_method_handler(wrapper)
```

### Concurrency limiter (simpler than rate limiting)

Instead of tracking requests per second, just limit how many RPCs run at the same time. Simpler to reason about, and directly prevents thread exhaustion.

```python
class ConcurrencyLimitInterceptor(grpc.ServerInterceptor):
    def __init__(self, max_concurrent=100):
        self.semaphore = threading.Semaphore(max_concurrent)

    def intercept_service(self, continuation, handler_call_details):
        def wrapper(request, context):
            # Try to acquire immediately — do not queue
            if not self.semaphore.acquire(blocking=False):
                context.abort(
                    grpc.StatusCode.RESOURCE_EXHAUSTED,
                    'server at capacity — try again later'
                )
                return
            try:
                return continuation(handler_call_details)(request, context)
            finally:
                self.semaphore.release()  # always release, even on exception

        return grpc.unary_unary_rpc_method_handler(wrapper)
```

### Throttling with retry hint (tell client when to retry)

The rich error model lets you tell the client exactly how long to wait before retrying.

```python
from grpc_status import rpc_status
from google.rpc import status_pb2, error_details_pb2

class SmartRateLimitInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        def wrapper(request, context):
            if not self.limiter.allow():
                # Tell client to retry after 2 seconds
                retry_info = error_details_pb2.RetryInfo()
                retry_info.retry_delay.seconds = 2

                rich_status = status_pb2.Status(
                    code=grpc.StatusCode.RESOURCE_EXHAUSTED.value[0],
                    message='rate limit exceeded',
                    details=[retry_info]  # structured retry hint
                )
                context.abort_with_status(rpc_status.to_status(rich_status))
                return
            return continuation(handler_call_details)(request, context)
        return grpc.unary_unary_rpc_method_handler(wrapper)
```

### Rate limiting with Redis (distributed, across multiple server instances)

Local in-memory rate limiting only works for 1 server. If you have 10 pods, each has its own counter — effective limit is 10x your intended limit. Use Redis for shared state.

```python
import redis

class RedisRateLimiter:
    def __init__(self, redis_client, rate_per_second):
        self.redis = redis_client
        self.rate = rate_per_second

    def allow(self, client_id):
        key = f'rate:{client_id}:{int(time.time())}'  # per-second window
        count = self.redis.incr(key)
        if count == 1:
            self.redis.expire(key, 2)  # expire after 2 seconds
        return count <= self.rate


redis_client = redis.Redis(host='redis', port=6379)
limiter = RedisRateLimiter(redis_client, rate_per_second=1000)

class DistributedRateLimitInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        def wrapper(request, context):
            client_id = dict(context.invocation_metadata()).get('x-client-id', 'unknown')
            if not limiter.allow(client_id):
                context.abort(grpc.StatusCode.RESOURCE_EXHAUSTED, 'rate limit exceeded')
                return
            return continuation(handler_call_details)(request, context)
        return grpc.unary_unary_rpc_method_handler(wrapper)
```

> **Rate limiting summary:**
> - Use `RESOURCE_EXHAUSTED` status code — never `INTERNAL` or `UNAVAILABLE`
> - Do NOT add `RESOURCE_EXHAUSTED` to client retry lists — retrying an overloaded server makes it worse
> - For 1 pod: in-memory token bucket is fine
> - For multiple pods: use Redis or a service mesh (Envoy has built-in rate limiting)
> - Fail fast and reject immediately — never queue requests when overloaded

---

## 8. Circuit Breaking

### What is it and why you need it

Retry is great for brief network blips. But if a downstream service is genuinely struggling for 30 seconds, retrying every failed RPC means you are hammering it with traffic while it tries to recover. This keeps it dead longer.

A circuit breaker watches the error rate to a downstream service. When errors get too high, it "opens" — all requests to that service immediately fail without even trying the network. After a cooldown period it "half-opens" and allows one test request through. If that succeeds, the circuit closes and normal traffic resumes.

```
CLOSED (normal):  all RPCs flow through normally
       ↓ error rate > threshold (e.g. >50% for 10s)
OPEN (broken):    all RPCs immediately fail (UNAVAILABLE) — no network calls
       ↓ after cooldown period (e.g. 30s)
HALF-OPEN:        1 test RPC allowed through
       ↓ success                ↓ failure
CLOSED again      OPEN again (reset cooldown)
```

### Simple circuit breaker implementation

```python
import time
import threading
from enum import Enum

class CircuitState(Enum):
    CLOSED = 'closed'       # normal operation
    OPEN = 'open'           # failing fast
    HALF_OPEN = 'half_open' # testing recovery

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=30):
        self.failure_threshold = failure_threshold  # failures before opening
        self.recovery_timeout = recovery_timeout    # seconds before half-open
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.lock = threading.Lock()

    def call(self, fn, *args, **kwargs):
        with self.lock:
            if self.state == CircuitState.OPEN:
                elapsed = time.monotonic() - self.last_failure_time
                if elapsed > self.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                else:
                    raise grpc.RpcError('circuit open — service unavailable')

        try:
            result = fn(*args, **kwargs)
            with self.lock:
                # Success — reset
                self.failure_count = 0
                self.state = CircuitState.CLOSED
            return result

        except grpc.RpcError as e:
            with self.lock:
                self.failure_count += 1
                self.last_failure_time = time.monotonic()
                if self.failure_count >= self.failure_threshold:
                    self.state = CircuitState.OPEN
            raise


# Usage in your service handler
payment_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30)

def charge_user(user_id, amount):
    try:
        return payment_breaker.call(
            payment_stub.Charge,
            ChargeRequest(user_id=user_id, amount=amount),
            timeout=2.0
        )
    except grpc.RpcError as e:
        if 'circuit open' in str(e):
            # Return fallback or cached response
            return ChargeResponse(success=False, reason='payment service unavailable')
        raise
```

> **In production:** Use a service mesh (Istio, Linkerd) or Envoy proxy for circuit breaking. They implement it at the infrastructure level with no code changes, better metrics, and more sophisticated algorithms.

---

## 9. Interceptors — Your Middleware Layer

Every cross-cutting concern — auth, logging, tracing, metrics, rate limiting — belongs in an interceptor, not in your handler code. Interceptors keep handlers clean and ensure nothing is accidentally skipped.

### Server interceptor chain — order matters

```python
server = grpc.server(
    executor,
    interceptors=[
        AuthInterceptor(),          # 1st — reject unauthenticated fast, before any work
        AuthorizationInterceptor(), # 2nd — reject unauthorized, before any DB calls
        RateLimitInterceptor(),     # 3rd — reject over-quota fast
        TracingInterceptor(),       # 4th — start trace span (now we know who the caller is)
        LoggingInterceptor(),       # 5th — log with trace ID and user ID
        MetricsInterceptor(),       # 6th — time everything including the interceptors above
    ]
)
```

### Metrics interceptor — capture everything

```python
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    'grpc_requests_total',
    'Total gRPC requests',
    ['method', 'status']
)
REQUEST_LATENCY = Histogram(
    'grpc_request_duration_seconds',
    'gRPC request latency',
    ['method'],
    buckets=[.005, .01, .025, .05, .1, .25, .5, 1, 2.5, 5]
)

class MetricsInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        method = handler_call_details.method  # e.g. /UserService/GetUser

        def wrapper(request, context):
            start = time.monotonic()
            status = 'OK'
            try:
                response = continuation(handler_call_details)(request, context)
                return response
            except Exception:
                code = context.code()
                status = code.name if code else 'UNKNOWN'
                raise
            finally:
                latency = time.monotonic() - start
                REQUEST_COUNT.labels(method=method, status=status).inc()
                REQUEST_LATENCY.labels(method=method).observe(latency)

        return grpc.unary_unary_rpc_method_handler(wrapper)
```

---

## 10. Security — TLS, mTLS, Auth

### Never use insecure_channel in production

```python
# WRONG for production
channel = grpc.insecure_channel('userservice:50051')

# CORRECT — TLS
credentials = grpc.ssl_channel_credentials(
    root_certificates=open('ca.crt', 'rb').read()
)
channel = grpc.secure_channel('userservice:443', credentials)

# Server
server_credentials = grpc.ssl_server_credentials([(
    open('server.key', 'rb').read(),
    open('server.crt', 'rb').read(),
)])
server.add_secure_port('[::]:443', server_credentials)
```

### mTLS — mutual authentication (gold standard for service-to-service)

Regular TLS: client verifies server identity.
mTLS: both sides verify each other. An unauthorized pod cannot even complete the TCP handshake.

```python
# Server — requires client certificate
server_credentials = grpc.ssl_server_credentials(
    [(open('server.key', 'rb').read(), open('server.crt', 'rb').read())],
    root_certificates=open('ca.crt', 'rb').read(),
    require_client_auth=True   # reject any client without a valid cert
)

# Client — sends its own certificate
client_credentials = grpc.ssl_channel_credentials(
    root_certificates=open('ca.crt', 'rb').read(),
    private_key=open('client.key', 'rb').read(),
    certificate_chain=open('client.crt', 'rb').read(),
)
channel = grpc.secure_channel('userservice:443', client_credentials)
```

> In Kubernetes with Istio or Linkerd, mTLS is automatic. The sidecar handles certificate rotation and verification. Your app code just uses insecure channels to `localhost` (the sidecar). No cert management in your code at all — this is the recommended approach.

### JWT authentication via interceptor

```python
import jwt

class AuthInterceptor(grpc.ServerInterceptor):
    PUBLIC_KEY = open('public.pem', 'rb').read()

    # These methods do not require auth
    PUBLIC_METHODS = {'/grpc.health.v1.Health/Check'}

    def intercept_service(self, continuation, handler_call_details):
        def wrapper(request, context):
            if handler_call_details.method in self.PUBLIC_METHODS:
                return continuation(handler_call_details)(request, context)

            metadata = dict(context.invocation_metadata())
            token = metadata.get('authorization', '').replace('Bearer ', '')

            if not token:
                context.abort(grpc.StatusCode.UNAUTHENTICATED, 'missing token')
                return

            try:
                claims = jwt.decode(token, self.PUBLIC_KEY, algorithms=['RS256'])
                # Attach to context so handlers and downstream interceptors can read it
                context.user_id = claims['sub']
                context.user_roles = claims.get('roles', [])
            except jwt.ExpiredSignatureError:
                context.abort(grpc.StatusCode.UNAUTHENTICATED, 'token expired')
                return
            except jwt.InvalidTokenError:
                context.abort(grpc.StatusCode.UNAUTHENTICATED, 'invalid token')
                return

            return continuation(handler_call_details)(request, context)

        return grpc.unary_unary_rpc_method_handler(wrapper)
```

---

## 11. Authorization

Authentication answers "who are you?" Authorization answers "are you allowed to do this?"

```python
# Permission map — which roles can call which methods
METHOD_PERMISSIONS = {
    '/UserService/GetUser':    ['user', 'admin'],
    '/UserService/DeleteUser': ['admin'],
    '/UserService/ListUsers':  ['admin', 'support'],
}

class AuthorizationInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        def wrapper(request, context):
            method = handler_call_details.method
            required_roles = METHOD_PERMISSIONS.get(method)

            if required_roles is None:
                # Method not in map — allow (or deny, depending on your policy)
                return continuation(handler_call_details)(request, context)

            user_roles = getattr(context, 'user_roles', [])
            if not any(role in required_roles for role in user_roles):
                context.abort(
                    grpc.StatusCode.PERMISSION_DENIED,
                    f'role required: {required_roles}'
                )
                return

            return continuation(handler_call_details)(request, context)

        return grpc.unary_unary_rpc_method_handler(wrapper)
```

> For large-scale systems, avoid hardcoding roles. Use **Open Policy Agent (OPA)** — a policy engine that evaluates permissions from a separate policy file. Your interceptor just calls OPA's local HTTP API and gets a yes/no decision. Policy changes deploy without code changes.

---

## 12. Error Handling — Use the Right Status Codes

Return the right status code. Client retry logic, alerting dashboards, and SLO calculations all depend on it.

| Status code | Use for | Retry? |
|---|---|---|
| `OK` | Success | No |
| `INVALID_ARGUMENT` | Bad input data (missing field, wrong type) | No — fix the request |
| `NOT_FOUND` | Resource does not exist | No |
| `ALREADY_EXISTS` | Tried to create a duplicate | No |
| `PERMISSION_DENIED` | Authenticated but not allowed | No |
| `UNAUTHENTICATED` | No valid token | No — get a token first |
| `RESOURCE_EXHAUSTED` | Rate limited or quota exceeded | No — back off |
| `UNAVAILABLE` | Server temporarily down, pod restarting | Yes |
| `DEADLINE_EXCEEDED` | Timed out | Only if idempotent |
| `FAILED_PRECONDITION` | System not in correct state (e.g. account frozen) | No |
| `ABORTED` | Conflict (e.g. optimistic locking failed) | Yes — retry the transaction |
| `INTERNAL` | Unexpected server error / bug / panic | No — fix the bug |
| `UNIMPLEMENTED` | Method not found | No |

**The most important rule:** Never return `INTERNAL` for business logic errors. `INTERNAL` means "my code panicked or hit an unexpected state." Use `FAILED_PRECONDITION`, `ABORTED`, or `INVALID_ARGUMENT` for business failures.

```python
def DeleteUser(self, request, context):
    user = db.get_user(request.id)

    # WRONG — leaking DB error as INTERNAL
    if not user:
        context.abort(grpc.StatusCode.INTERNAL, str(db_error))

    # CORRECT — map to meaningful status code
    if not user:
        context.abort(grpc.StatusCode.NOT_FOUND, f'user {request.id} not found')
        return

    if user.account_frozen:
        context.abort(grpc.StatusCode.FAILED_PRECONDITION, 'account is frozen')
        return

    db.delete_user(request.id)
    return DeleteUserResponse(success=True)
```

---

## 13. Rich Error Model

Basic status codes are not enough for clients to handle errors intelligently. Use Google's rich error model to send structured error details.

```python
from grpc_status import rpc_status
from google.rpc import status_pb2, error_details_pb2

def CreateUser(self, request, context):
    violations = []

    if not request.name:
        violations.append(error_details_pb2.BadRequest.FieldViolation(
            field='name', description='name is required'
        ))
    if not request.email or '@' not in request.email:
        violations.append(error_details_pb2.BadRequest.FieldViolation(
            field='email', description='must be a valid email address'
        ))

    if violations:
        bad_request = error_details_pb2.BadRequest(field_violations=violations)
        rich_status = status_pb2.Status(
            code=grpc.StatusCode.INVALID_ARGUMENT.value[0],
            message='validation failed',
            details=[bad_request]
        )
        context.abort_with_status(rpc_status.to_status(rich_status))
        return

    # For rate limit errors — tell client when to retry
    if not rate_limiter.allow():
        retry_info = error_details_pb2.RetryInfo()
        retry_info.retry_delay.seconds = 5
        rich_status = status_pb2.Status(
            code=grpc.StatusCode.RESOURCE_EXHAUSTED.value[0],
            message='rate limit exceeded',
            details=[retry_info]
        )
        context.abort_with_status(rpc_status.to_status(rich_status))
        return
```

```python
# Client reads the structured error
try:
    response = stub.CreateUser(request)
except grpc.RpcError as e:
    status = rpc_status.from_call(e)
    if status:
        for detail in status.details:
            if detail.Is(error_details_pb2.BadRequest.DESCRIPTOR):
                bad_req = error_details_pb2.BadRequest()
                detail.Unpack(bad_req)
                for v in bad_req.field_violations:
                    print(f'Field {v.field}: {v.description}')
            elif detail.Is(error_details_pb2.RetryInfo.DESCRIPTOR):
                retry = error_details_pb2.RetryInfo()
                detail.Unpack(retry)
                wait = retry.retry_delay.seconds
                print(f'Retry after {wait} seconds')
```

---

## 14. Payload Optimization

### Use bytes, not base64 strings

Base64 increases payload size by 33% and wastes CPU on encode/decode.

```proto
// WRONG
message UploadRequest {
  string file_data = 1;   // base64 string — 33% bigger, slower
}

// CORRECT
message UploadRequest {
  bytes file_data = 1;    // raw binary — compact and fast
}
```

### Use proper types — not strings for everything

```proto
// WRONG
message Event {
  string timestamp = 1;   // "2024-01-15T10:30:00Z" — wastes bytes, breaks sorting
  string user_id   = 2;   // "12345" — wastes bytes
}

// CORRECT
import "google/protobuf/timestamp.proto";

message Event {
  google.protobuf.Timestamp timestamp = 1;  // compact, timezone-safe
  int64 user_id = 2;                        // 8 bytes max
}
```

### Stream large data — never send big payloads in one message

```proto
// WRONG — single message with large file
rpc UploadFile(UploadRequest) returns (UploadResponse);

// CORRECT — stream in small chunks
rpc UploadFile(stream FileChunk) returns (UploadResponse);

message FileChunk {
  bytes data     = 1;   // 32KB per chunk
  int32 chunk_id = 2;
  bool  is_last  = 3;
}
```

```python
def upload_file(stub, file_path, chunk_size=32768):  # 32KB chunks
    def chunk_generator():
        with open(file_path, 'rb') as f:
            chunk_id = 0
            while True:
                data = f.read(chunk_size)
                if not data:
                    break
                is_last = len(data) < chunk_size
                yield FileChunk(data=data, chunk_id=chunk_id, is_last=is_last)
                chunk_id += 1

    return stub.UploadFile(chunk_generator())
```

### Enable compression for repetitive data

```python
# Client — compress outgoing requests
response = stub.GetUser(
    UserRequest(id=42),
    compression=grpc.Compression.Gzip
)

# Server — compress responses
server = grpc.server(executor, compression=grpc.Compression.Gzip)
```

> Use compression only for highly repetitive data (JSON-like structures, text). For already-compressed data (images, video) it wastes CPU with no size benefit. Always benchmark before enabling globally.

### Protobuf evolution — never break compatibility

```proto
message User {
  int32  id    = 1;   // NEVER change field number or type
  string name  = 2;   // NEVER change field number or type
  // string phone = 3;  // deleted — NEVER reuse field number 3
  reserved 3;           // lock the number so nobody reuses it
  reserved "phone";     // lock the name too

  string email = 4;   // new field added — old clients ignore it safely
}
```

---

## 15. Flow Control and Backpressure

HTTP/2 has built-in flow control. When a client sends too fast, the server sends `WINDOW_UPDATE` frames to slow it down. But you still need to configure server limits.

```python
server = grpc.server(executor, options=[
    # Max RPCs running at the same time — queue beyond this
    ('grpc.max_concurrent_rpcs', 200),

    # Max incoming message size — prevent memory bombs
    ('grpc.max_receive_message_length', 4 * 1024 * 1024),  # 4MB

    # Max outgoing message size
    ('grpc.max_send_message_length', 4 * 1024 * 1024),     # 4MB
])
```

### Load shedding — fail fast, not slow

When your server is overloaded, do not queue requests. Queue = increased latency = client deadlines expire = server processes the request for a client that already gave up = wasted CPU.

Reject immediately with `RESOURCE_EXHAUSTED` and let the client retry or show a degraded response.

```python
import psutil

class LoadSheddingInterceptor(grpc.ServerInterceptor):
    CPU_THRESHOLD = 85  # percent

    def intercept_service(self, continuation, handler_call_details):
        def wrapper(request, context):
            cpu = psutil.cpu_percent(interval=None)
            if cpu > self.CPU_THRESHOLD:
                context.abort(
                    grpc.StatusCode.RESOURCE_EXHAUSTED,
                    f'server overloaded (cpu={cpu:.0f}%) — try again later'
                )
                return
            return continuation(handler_call_details)(request, context)
        return grpc.unary_unary_rpc_method_handler(wrapper)
```

---

## 16. Streaming Best Practices

### Always check if the client is still connected

```python
def ListOrders(self, request, context):
    for order in db.stream_orders(request.user_id):  # DB cursor
        # Check before every yield — client may have cancelled or timed out
        if not context.is_active():
            return   # close DB cursor, free resources immediately

        yield OrderResponse(order=order)
```

Without this check: client cancels, server keeps querying the DB and building responses into the void. Every resource held until the full query completes.

### Set deadlines even on streaming RPCs

```python
# Client — stream with a maximum total duration
responses = stub.ListOrders(
    OrderRequest(user_id=42),
    timeout=30.0   # entire stream must complete within 30 seconds
)
for response in responses:
    process(response)
```

### Replace many short unary calls with streaming

```python
# WRONG under high frequency — new RPC overhead for each price update
while True:
    price = stub.GetPrice(PriceRequest(symbol='BTC'), timeout=1.0)
    display(price)
    time.sleep(0.1)

# CORRECT — one RPC, server streams updates
def watch_prices(stub):
    for price_update in stub.WatchPrice(PriceRequest(symbol='BTC'), timeout=300):
        display(price_update)
        # HTTP/2 flow control handles backpressure automatically
```

> Use streaming to replace polling patterns. One long-lived stream is far cheaper than thousands of short unary RPCs — no repeated connection overhead, no load balancing cost per call.
>
> Exception: avoid streaming in Python unless necessary — see Section 4.

---

## 17. Health Checks

Use the standard gRPC health protocol. Kubernetes, Envoy, and load balancers all understand it.

```python
from grpc_health.v1 import health, health_pb2, health_pb2_grpc

health_servicer = health.HealthServicer()

# Register with server
health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)

# Mark as healthy when ready
health_servicer.set('UserService', health_pb2.HealthCheckResponse.SERVING)

# Mark as NOT_SERVING before shutdown — load balancer stops routing first
def handle_sigterm(sig, frame):
    health_servicer.set('UserService', health_pb2.HealthCheckResponse.NOT_SERVING)
    time.sleep(5)          # wait for LB to detect and stop routing
    server.stop(grace=30)  # then finish in-flight RPCs
    sys.exit(0)
```

```yaml
# Kubernetes probes — use grpc, not httpGet
livenessProbe:
  grpc:
    port: 50051
    service: UserService
  initialDelaySeconds: 5
  periodSeconds: 10

readinessProbe:
  grpc:
    port: 50051
    service: UserService
  initialDelaySeconds: 5
  periodSeconds: 5
```

---

## 18. Observability — Metrics, Tracing, Logging

### RED metrics — the minimum to track

RED = **R**ate, **E**rrors, **D**uration. These three tell you the health of any gRPC service.

```python
# Prometheus metrics to expose
grpc_requests_total{service, method, status}    # Rate + Error rate
grpc_request_duration_seconds{service, method}  # Duration (use histogram for p50/p95/p99)
```

**Alert on:**
- Error rate > 1% sustained for 2 minutes
- p99 latency > your SLO threshold
- Sudden drop in request rate (client crash, not low traffic)

### Distributed tracing with OpenTelemetry

```python
from opentelemetry import trace
from opentelemetry.instrumentation.grpc import GrpcInstrumentorServer, GrpcInstrumentorClient
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Setup — do this once at startup
provider = TracerProvider()
provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint='http://otel-collector:4317'))
)
trace.set_tracer_provider(provider)

# Auto-instrument all gRPC calls — no changes to handlers needed
GrpcInstrumentorServer().instrument()   # server side
GrpcInstrumentorClient().instrument()   # client side

# Now every RPC automatically gets:
# - trace_id propagated via metadata across service boundaries
# - span per RPC with method, status, latency
# - parent-child span links across services
# View in Jaeger, Zipkin, or Grafana Tempo
```

Without tracing, when a request takes 3 seconds across 5 services, you cannot tell which service added the latency. With tracing you see the exact span that was slow.

### Structured logging — always include trace ID

```python
import structlog

log = structlog.get_logger()

class LoggingInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        def wrapper(request, context):
            span = trace.get_current_span()
            trace_id = format(span.get_span_context().trace_id, '032x')
            start = time.monotonic()

            try:
                response = continuation(handler_call_details)(request, context)
                log.info('rpc.success',
                    method=handler_call_details.method,
                    trace_id=trace_id,
                    peer=context.peer(),
                    latency_ms=round((time.monotonic() - start) * 1000, 2)
                )
                return response
            except Exception as e:
                log.error('rpc.error',
                    method=handler_call_details.method,
                    trace_id=trace_id,
                    status=str(context.code()),
                    latency_ms=round((time.monotonic() - start) * 1000, 2)
                )
                raise
        return grpc.unary_unary_rpc_method_handler(wrapper)
```

> Never log an RPC without `trace_id`. Without it you cannot correlate a log entry in Service A with the corresponding entry in Service B, C, or D.

---

## 19. Graceful Shutdown

Every Kubernetes rolling deploy sends SIGTERM to your pod. Without a graceful shutdown handler, every in-flight RPC at deploy time gets a hard TCP reset and clients see errors.

```python
import signal
import sys

server = grpc.server(executor)
server.start()

def handle_sigterm(signum, frame):
    print('SIGTERM received — starting graceful shutdown')

    # Step 1: Mark as NOT_SERVING so load balancer stops routing here
    health_servicer.set('UserService', health_pb2.HealthCheckResponse.NOT_SERVING)

    # Step 2: Wait for LB health checks to detect the change (2-5 seconds)
    time.sleep(5)

    # Step 3: Stop accepting new RPCs, wait up to 30s for in-flight ones to finish
    done = server.stop(grace=30)
    done.wait(timeout=30)
    print('Shutdown complete')
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_sigterm)
signal.signal(signal.SIGINT, handle_sigterm)
server.wait_for_termination()
```

```yaml
# Kubernetes — preStop hook adds a delay before SIGTERM
# This gives k8s time to remove the pod from Service endpoints first
spec:
  containers:
    - name: userservice
      lifecycle:
        preStop:
          exec:
            command: ["/bin/sleep", "5"]
      terminationGracePeriodSeconds: 60   # must be > grace period in server.stop()
```

**Shutdown sequence:**
```
k8s sends SIGTERM
  → preStop hook: sleep 5s  (pod still receiving traffic)
  → SIGTERM fires: health = NOT_SERVING  (LB stops routing)
  → sleep 5s  (LB detects change, drains in-flight requests)
  → server.stop(grace=30)  (reject new, finish existing)
  → all done → pod exits cleanly
```

---

## 20. Production Checklist

```
CONNECTION
  ✓ One channel per target service, created at startup, reused always
  ✓ Channel pool for very high concurrency (>100 concurrent RPCs)
  ✓ keepalive_time_ms set on channel (10s recommended)
  ✓ keepalive_timeout_ms set on channel (5s recommended)
  ✓ keepalive_permit_without_calls = True
  ✓ Server keepalive_min_time_ms configured to match client
  ✓ max_receive_message_length and max_send_message_length set (4MB default)

LOAD BALANCING
  ✓ NOT using ClusterIP Service for gRPC in Kubernetes
  ✓ Headless Service + round_robin OR service mesh (Istio/Linkerd)
  ✓ round_robin explicitly configured in service_config
  ✓ L7 load balancer if using cloud ALB (not NLB)

CONCURRENCY
  ✓ Python: using grpc.aio for services with >100 RPS
  ✓ ThreadPoolExecutor max_workers sized to expected concurrency
  ✓ Not using Python streaming unless necessary

RESILIENCE
  ✓ Deadline set on every single RPC — no exceptions
  ✓ Deadline propagated to all downstream calls
  ✓ Retry only on UNAVAILABLE for idempotent methods
  ✓ maxAttempts ≤ 3 with exponential backoff
  ✓ RESOURCE_EXHAUSTED not in retryableStatusCodes
  ✓ Circuit breaker for downstream dependencies (service mesh or library)

RATE LIMITING
  ✓ RateLimitInterceptor on server with token bucket or concurrency limit
  ✓ Returns RESOURCE_EXHAUSTED (not INTERNAL or UNAVAILABLE)
  ✓ Per-client limits for multi-tenant services
  ✓ Redis-based distributed limiter if running multiple pods
  ✓ Load shedding under CPU/memory pressure (fail fast)

SECURITY
  ✓ TLS or mTLS in production (never insecure_channel)
  ✓ mTLS via service mesh (no cert management in code)
  ✓ Auth interceptor validates JWT on every RPC
  ✓ Auth interceptor skips public methods (health check)
  ✓ AuthZ interceptor checks method-level permissions
  ✓ UNAUTHENTICATED for missing/invalid token
  ✓ PERMISSION_DENIED for valid token but wrong role

ERROR HANDLING
  ✓ Correct status codes (not INTERNAL for business errors)
  ✓ Rich error model for validation errors (BadRequest field violations)
  ✓ RetryInfo in RESOURCE_EXHAUSTED responses
  ✓ No raw stack traces or DB errors sent to clients

PAYLOAD
  ✓ bytes instead of base64 strings
  ✓ google.protobuf.Timestamp for dates
  ✓ Streaming for data > 1MB
  ✓ Field numbers never changed or reused (reserved for deleted fields)
  ✓ Compression enabled only for repetitive data

OBSERVABILITY
  ✓ MetricsInterceptor: rate, error rate, latency histogram (p50/p95/p99)
  ✓ OpenTelemetry auto-instrumentation on both client and server
  ✓ trace_id in every log line
  ✓ Alerts: error rate > 1%, p99 latency > threshold, request rate drop

OPERATIONS
  ✓ Standard gRPC health check protocol (grpc.health.v1)
  ✓ SIGTERM handler → NOT_SERVING → sleep 5s → server.stop(grace=30)
  ✓ Kubernetes preStop hook (sleep 5)
  ✓ terminationGracePeriodSeconds > server.stop grace period
  ✓ context.is_active() checked in all streaming handlers
  ✓ Deadline set on streaming RPCs too
```

---

## The Most Common Production Failures

In order of how often they occur:

1. **Silent TCP drops** — no keepalive → RPCs hang mysteriously during quiet periods
2. **All traffic on one pod** — ClusterIP + pick_first → hot spots, other pods idle
3. **Cascading timeouts** — deadline not propagated → downstream keeps working after client gave up
4. **Invisible errors** — no metrics interceptor → nobody knows the error rate until users complain
5. **Retry storms** — retrying RESOURCE_EXHAUSTED → overloaded server gets hammered while trying to recover
6. **Deploy-time errors** — no graceful shutdown → users see errors on every deploy
7. **Memory crashes** — no message size limit → one large request OOMs the server
8. **Wrong status codes** — INTERNAL for everything → retry logic and alerts break

---

*Sources: gRPC official documentation · gRPC Performance Best Practices · Google API Design Guide · Production experience*