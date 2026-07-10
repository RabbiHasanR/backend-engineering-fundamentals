# gRPC — Complete Reference Guide
> From Channel to TCP — Everything in One Place

**Topics covered:** Channels · Subchannels · TCP · HTTP/2 Multiplexing · Load Balancing · Interceptors · Deadline · Retry · Cancellation · Termination

---

## Table of Contents

1. [What is gRPC?](#1-what-is-grpc)
2. [The .proto File and Code Generation](#2-the-proto-file-and-code-generation)
3. [The 4 Types of gRPC Communication](#3-the-4-types-of-grpc-communication)
4. [Core Architecture — Channel, Subchannel, TCP, HTTP/2](#4-core-architecture--channel-subchannel-tcp-http2)
5. [Stub and Interceptors](#5-stub-and-interceptors)
6. [Deadline, Cancellation, Retry, Termination](#6-deadline-cancellation-retry-termination)
7. [Complete Request/Response Lifecycle](#7-complete-requestresponse-lifecycle)
8. [Complete Mental Model](#8-complete-mental-model)
9. [Quick Reference](#9-quick-reference)

---

## 1. What is gRPC?

gRPC is an open-source, high-performance Remote Procedure Call (RPC) framework built by Google. It lets services call functions on another machine exactly like calling a local function — but across a network, across different languages, and across platforms.

> **Think of it as:** call a function on another server the same way you call a local function in your code. The network complexity is completely hidden.

gRPC is the industry standard for microservice-to-microservice communication, used by Google, Netflix, Cloudflare, and thousands of engineering teams worldwide.

### Why gRPC is fast — two technologies working together

| HTTP/2 — transport layer | Protocol Buffers — data format |
|---|---|
| Binary framing (not plain text) | Binary serialization — up to 10x smaller than JSON |
| Multiplexing — many RPCs on 1 TCP connection | Strongly typed — no field ambiguity |
| Header compression — less overhead per request | `protoc` generates client + server code |
| Bi-directional streaming built-in | Language-neutral — Python server, Go client |
| Persistent connections — no reconnect per request | Schema-enforced contracts between teams |

### gRPC vs REST

| Feature | REST + JSON | gRPC + Protobuf |
|---|---|---|
| Transport | HTTP/1.1 — 1 request per TCP | HTTP/2 — many requests per TCP |
| Data format | Text (JSON) — human readable | Binary (protobuf) — compact, fast |
| Speed | Moderate | Much faster (binary + multiplexing) |
| Streaming | Limited (SSE, long-poll hacks) | Built-in — 4 native types |
| Code generation | No — manual client code | Yes — `protoc` generates stubs |
| Type safety | No — runtime errors | Yes — compile-time contract |
| Browser support | Universal | Limited — needs grpc-web proxy |
| Best for | Public APIs, simple CRUD | Internal microservices, high throughput |

---

## 2. The .proto File and Code Generation

Everything in gRPC starts from a `.proto` file. You define your service and messages once, run `protoc` at build time, and it generates native code for every language. This generated code lives in your project like any other source file — it does **NOT** regenerate on every request.

```proto
// user.proto — define once, generate everywhere
edition = "2023";

service UserService {
  rpc GetUser     (UserRequest)          returns (UserResponse);        // unary
  rpc ListUsers   (ListRequest)          returns (stream UserResponse); // server stream
  rpc CreateUsers (stream UserRequest)   returns (CreateResponse);      // client stream
  rpc SyncUsers   (stream UserRequest)   returns (stream UserResponse); // bidi stream
}

message UserRequest  { int32  id    = 1; }
message UserResponse { int32  id    = 1; string name = 2; string email = 3; }
```

```bash
# Run once at build time — NOT per request
protoc --python_out=./server --grpc_python_out=./server user.proto   # server side
protoc --go_out=./client    --go-grpc_out=./client    user.proto    # client side

# Server gets:  user_pb2.py (message classes)  +  user_pb2_grpc.py (servicer base)
# Client gets:  user.pb.go  (message structs)  +  user_grpc.pb.go  (stub)
```

> **Key rule — both sides must run `protoc` from the same `.proto` file.**
> Server and client can be different languages. Because both are generated from the same contract, their binary encoding is identical on the wire. Language-neutral by design.

---

## 3. The 4 Types of gRPC Communication

| Type | Pattern | Proto syntax | Use case |
|---|---|---|---|
| **Unary** | 1 request → 1 response | `rpc Get(Req) returns (Res)` | Fetch user, auth token, simple lookup |
| **Server streaming** | 1 request → many responses | `returns (stream Res)` | Large dataset, live events, stock feed |
| **Client streaming** | Many requests → 1 response | `rpc Upload(stream Req) returns (Res)` | File upload in chunks, batch insert |
| **Bidirectional** | Many ↔ many (independent) | `stream Req → stream Res` | Real-time chat, game state, live collab |

The table above says *what* each type is. What matters for architecture is *how* each one
behaves on the wire — how it maps onto the `channel → subchannel → TCP → HTTP/2 stream` model
built in Section 4. The single rule that governs all four:

> **One RPC call = exactly one HTTP/2 stream.**
> A stream carries one logical call from start to finish. You cannot pack multiple RPCs into
> one stream, and a streaming RPC does **not** open a new stream per message — it keeps its
> *one* stream open and sends more frames on it. The only difference between the 4 types is
> **how many messages flow each way** on that single stream, and **when** the stream half-closes.

---

### 3.1 Unary — one message each way

The simplest case: the entire request is serialized once and sent in a single shot. The client
opens one stream, sends a `HEADERS` frame (method, path, deadline, metadata) followed by one
`DATA` frame carrying the whole protobuf body, and immediately half-closes the stream with
`END_STREAM` — it has nothing more to send. The server processes the full payload, then replies
with one `DATA` frame and closing trailers. One message up, one message down, done.

```
# Unary — single message each direction, on ONE stream

stub.GetUser(UserRequest(id=42), timeout=2.0)     # 1 RPC → stream ID 1

CLIENT ──────────────────────────────────────────────► SERVER
  [HEADERS stream=1]  :path=/UserService/GetUser
  [DATA    stream=1]  <full protobuf payload>  END_STREAM   ← half-close now
                                                            handler runs
CLIENT ◄────────────────────────────────────────────── SERVER
  [HEADERS stream=1]  :status=200
  [DATA    stream=1]  <full response payload>
  [HEADERS stream=1]  grpc-status=0 (trailers)  END_STREAM
```

> **1 RPC = 1 stream = 1 request message + 1 response message.** The full payload goes over
> the wire at once, not piece by piece. This is the exact flow traced end-to-end (interceptors,
> Picker, serialization, deadline) in [Section 7](#7-complete-requestresponse-lifecycle) — refer
> there for the complete lifecycle rather than repeating it here.

---

### 3.2 Client Streaming — many messages up, one stream, one response

Client streaming is where the "1 RPC = 1 stream" rule matters most. A single call —
`rpc CreateUsers(stream UserRequest) returns (CreateResponse)` — opens **one** HTTP/2 stream and
**keeps it open**. The client then writes messages **one by one over time**, and each write
becomes its own `DATA` frame on that **same** stream ID. You are *not* opening a new RPC (or a
new stream) per chunk, and you cannot multiplex several RPCs onto this one stream — it belongs to
this single call until it ends.

When the client has sent everything, it half-closes the stream with `END_STREAM`. **Only then**
does the server compute and send back a **single** response message and trailers.

```
# Client streaming — N messages UP on ONE stream, 1 response DOWN

call = stub.CreateUsers(iter_of_requests)         # 1 RPC → stream ID 1

CLIENT ──────────────────────────────────────────────► SERVER
  [HEADERS stream=1]  :path=/UserService/CreateUsers
  [DATA    stream=1]  <chunk 1>        ┐
  [DATA    stream=1]  <chunk 2>        │ same stream, sent one by one
  [DATA    stream=1]  <chunk 3>        │ over time — NOT all at once
  ...                                  │
  [DATA    stream=1]  <chunk N>  END_STREAM   ← client half-closes
                                                server now builds 1 response
CLIENT ◄────────────────────────────────────────────── SERVER
  [HEADERS stream=1]  :status=200
  [DATA    stream=1]  <single CreateResponse>
  [HEADERS stream=1]  grpc-status=0 (trailers)  END_STREAM

# N chunks = N DATA frames on 1 stream — NOT N streams, NOT N RPCs.
```

In Python the streaming direction is expressed as an iterator/generator the client feeds into a
single call; the return value is one plain response object:

```python
def request_stream():
    yield UserRequest(id=1, name='Alice')     # each yield → one DATA frame
    yield UserRequest(id=2, name='Bob')       # same stream, sent sequentially
    yield UserRequest(id=3, name='Carol')     # client controls the pace

response = stub.CreateUsers(request_stream())  # ONE RPC, ONE stream
# stream stays open across all 3 yields, half-closes after the last one
response.created_count   # → 3   (a single response, only after half-close)
```

> **This entire streaming RPC is just one stream on the subchannel's TCP.** Per
> [Section 4.4](#44-http2-multiplexing--many-rpcs-on-1-tcp), other concurrent RPCs on the same
> TCP connection still get their own odd stream IDs (3, 5, 7…) and flow independently — a
> long-running client-stream on stream 1 never blocks them and never spills onto their streams.

---

### 3.3 Server Streaming — one request, many responses

Server streaming is the mirror image of client streaming. The client sends **one** request
message and half-closes immediately — just like unary. But the response side stays open: a
single call — `rpc ListUsers(ListRequest) returns (stream UserResponse)` — keeps **one** HTTP/2
stream open and the **server** writes messages **one by one over time**, each becoming its own
`DATA` frame on that **same** stream ID. The client does not poll and does not open a new RPC per
result — it reads from the one open stream until the server sends closing trailers with
`END_STREAM`, which marks the end of the sequence.

```
# Server streaming — 1 request UP, N messages DOWN on ONE stream

call = stub.ListUsers(ListRequest(page=1))        # 1 RPC → stream ID 1

CLIENT ──────────────────────────────────────────────► SERVER
  [HEADERS stream=1]  :path=/UserService/ListUsers
  [DATA    stream=1]  <full request payload>  END_STREAM   ← client half-closes
                                                            handler starts streaming
CLIENT ◄────────────────────────────────────────────── SERVER
  [HEADERS stream=1]  :status=200
  [DATA    stream=1]  <user 1>        ┐
  [DATA    stream=1]  <user 2>        │ same stream, sent one by one
  [DATA    stream=1]  <user 3>        │ over time — as the server produces them
  ...                                 │
  [DATA    stream=1]  <user N>        ┘
  [HEADERS stream=1]  grpc-status=0 (trailers)  END_STREAM   ← end of sequence

# N results = N DATA frames on 1 stream — NOT N streams, NOT N RPCs.
```

In Python the call returns an iterator; the client consumes results as they arrive instead of
waiting for a single value. The server's handler `yield`s each message:

```python
# CLIENT — iterate over the response stream as messages arrive
for user in stub.ListUsers(ListRequest(page=1)):   # ONE RPC, ONE stream
    print(user.name)        # each loop = one DATA frame off stream 1
# loop ends when server sends trailers (END_STREAM)

# SERVER — handler yields messages one by one
def ListUsers(self, request, context):
    for user in db.query_users(request.page):
        if not context.is_active():     # client gone? stop producing
            return
        yield UserResponse(id=user.id, name=user.name)   # → one DATA frame
```

> **1 request message up, many response messages down — all on one stream.** Backpressure is
> built in: HTTP/2 flow control pauses the server's writes if the client reads slowly, so a fast
> producer can't overwhelm a slow consumer. Per
> [Section 4.4](#44-http2-multiplexing--many-rpcs-on-1-tcp), this long-lived stream is still just
> one stream on the subchannel's TCP — other concurrent RPCs keep their own odd stream IDs
> (3, 5, 7…) and are never blocked by it.

---

### 3.4 Bidirectional Streaming — many ↔ many, independent

> _Coming soon._

---

## 4. Core Architecture — Channel, Subchannel, TCP, HTTP/2

This is the most important section. Understanding how `channel → subchannel → TCP → HTTP/2 streams` relate to each other explains everything about gRPC performance and behavior.

### 4.1 Channel — No TCP Yet

A channel is the first object you create. It holds the target address, credentials, and configuration. Creating a channel does **NOT** open a TCP connection. The channel sits in `IDLE` state until the first RPC is made.

```python
# Creating a channel — no TCP connection happens here
channel = grpc.insecure_channel('userservice.internal:50051')
# State: IDLE — no subchannel, no TCP, nothing on the network yet

# Channel states:
# IDLE              → created, no active RPCs, no connections
# CONNECTING        → trying to establish TCP connection
# READY             → TCP connected, can send RPCs
# TRANSIENT_FAILURE → connection failed, will retry
# SHUTDOWN          → channel.close() called, no more RPCs allowed
```

> **Channel = configuration object only.** One channel per target service. Created once at app start.
> The channel is reused for ALL RPCs to that service — not created per request.
> The channel manages subchannels internally — you never create subchannels directly.

---

### 4.2 Name Resolution — Translate Address to IPs

Before any TCP connection can be made, the channel's target name (like `userservice.internal`) must be resolved to real IP addresses. This is name resolution — essentially service discovery. It runs **once per channel**, not per RPC.

```python
# Your channel target:  userservice.internal:50051
# Name resolver asks DNS:
#   userservice.internal → [10.0.0.1, 10.0.0.2, 10.0.0.3]  (3 pods in Kubernetes)
# OR with 1 server:
#   userservice.internal → [10.0.0.1]                        (single server)

# Name resolver returns:
#   1. List of IP:port endpoints
#   2. Service config (retry policy, load balancer policy, etc.)
```

| Single server | 3 servers / 3 pods |
|---|---|
| DNS returns 1 IP | DNS returns 3 IPs (headless service) |
| `userservice.internal → [10.0.0.1:50051]` | `userservice.internal → [10.0.0.1, 10.0.0.2, 10.0.0.3]` |
| 1 IP = 1 subchannel = 1 TCP | 3 IPs = up to 3 subchannels |

Name resolution is pluggable. Default is DNS. You can plug in Consul, etcd, ZooKeeper, or any custom resolver by specifying a schema prefix in the target string (e.g. `consul://userservice`).

---

### 4.3 Load Balancer and Subchannels — TCP Connections

The load balancer receives the IP list from the name resolver and creates subchannels. Each subchannel is exactly **one TCP connection to one IP:port endpoint**. This is where real network connections are established.

> **The precise definition:** `subchannel = 1 resolved IP:port = 1 TCP connection = 1 HTTP/2 connection`
>
> The number of subchannels depends on: (a) how many IPs the name resolver returned, and (b) which load balancer policy is active.
>
> Subchannels are about servers, not about RPCs. RPCs are just HTTP/2 streams on existing subchannels.

#### Load balancer policies

| Policy | Subchannels created | RPC routing | Requires xDS? | When to use |
|---|---|---|---|---|
| `pick_first` (default) | 1 — tries IPs sequentially | All RPCs → same subchannel | No — native | Simple setup, 1 server |
| `round_robin` | 1 per IP in resolver list | RPCs rotate across subchannels | No — native | Multiple backends, even spread |
| `weighted_round_robin` | 1 per IP | More RPCs to faster backends | Yes — needs control plane | Heterogeneous server capacity |
| `least_request` | 1 per IP | RPCs → backend with fewest active | Yes — needs control plane | Variable request durations |

> **Native vs xDS policies**
> Out-of-the-box gRPC (no proxy, no control plane) natively supports `pick_first` and `round_robin` only. Advanced policies like `weighted_round_robin` and `least_request` require the client to be configured with **xDS** — Envoy's discovery service API — so it can receive dynamic load data (request rates, latency, backend health scores) from a control plane such as Istio or Traffic Director. Without xDS, those policies are not available in a proxyless thick-client setup.

#### How many subchannels with 1 server vs 3 servers

```python
# Scenario A — 1 server, pick_first (default)
# Name resolver returns: [10.0.0.1]
# Load balancer creates: 1 subchannel → 10.0.0.1:50051 → 1 TCP connection
# All RPCs from this client → same TCP → different HTTP/2 stream IDs

# Scenario B — 3 servers, pick_first (default) — connection-time fallback
# Name resolver returns: [10.0.0.1, 10.0.0.2, 10.0.0.3]
# pick_first tries IPs SEQUENTIALLY until one connects:
#   attempt 10.0.0.1 → unreachable? → try 10.0.0.2 → connected!
#   creates 1 subchannel → 10.0.0.2:50051 → locks onto this TCP forever
#   10.0.0.1 and 10.0.0.3 discarded — pick_first provides connection-time
#   fallback only, NOT per-request load balancing
# All RPCs → same subchannel → same TCP → different stream IDs

# Scenario C — 3 servers, round_robin
# Name resolver returns: [10.0.0.1, 10.0.0.2, 10.0.0.3]
# Load balancer creates: 3 subchannels → 3 TCP connections (one per IP)
# RPC 1 → subchannel A (stream 1 on TCP-A)
# RPC 2 → subchannel B (stream 1 on TCP-B)
# RPC 3 → subchannel C (stream 1 on TCP-C)
# RPC 4 → subchannel A (stream 3 on TCP-A)  ← rotates back

# Scenario D — 1 server with multiple IPs (rare)
# One physical machine, two network interfaces:
#   eth0 → 10.0.0.1,  eth1 → 10.0.0.2
# round_robin sees 2 IPs → creates 2 subchannels → 2 TCP to same machine
# pick_first sees 2 IPs → tries 10.0.0.1 first → if OK → 1 subchannel only
```

#### Multiple clients, 1 server — TCP count

```python
# Each client process creates its own channel and its own subchannels
# Client A → 1 channel → 1 subchannel → TCP connection A → Server
# Client B → 1 channel → 1 subchannel → TCP connection B → Server
# Client C → 1 channel → 1 subchannel → TCP connection C → Server

# Rule: N clients × M backend servers = N × M TCP connections total
# 100 client pods × 1 server  = 100 TCP connections on the server
# 100 client pods × 3 servers = 300 TCP connections total

# Each TCP connection carries unlimited concurrent RPCs via HTTP/2 multiplexing
```

#### Proxy / Kubernetes Service / Service Mesh (special case)

When a proxy (Envoy, Istio, nginx) or a Kubernetes ClusterIP Service sits in front of backends, the name resolver only ever sees **1 IP** — the proxy IP. The client creates 1 subchannel regardless of how many backend pods exist. The proxy handles all real load balancing. The gRPC client has no visibility into the backends.

```python
# With Kubernetes ClusterIP Service:
# Name resolver: userservice → 10.96.0.1 (virtual IP of k8s service)
# gRPC client: 1 subchannel → 10.96.0.1 → 1 TCP to k8s service
# k8s iptables: routes TCP to one of [pod1, pod2, pod3] — client unaware

# With Kubernetes Headless Service (direct pod IP routing):
# Name resolver: userservice → [10.244.1.1, 10.244.1.2, 10.244.1.3] (pod IPs)
# gRPC client: 3 subchannels → 3 TCP connections directly to pods
# This is true client-side load balancing — no proxy in between
```

#### Subchannel health monitoring

The load balancer continuously monitors every subchannel. If a server goes down, the subchannel TCP connection breaks. The load balancer detects this, tears down that subchannel, and creates a new one to a healthy endpoint. The channel object itself never changes — only internal subchannels are swapped.

---

### 4.4 HTTP/2 Multiplexing — Many RPCs on 1 TCP

Each subchannel is 1 TCP connection running HTTP/2. HTTP/2 introduces **streams** — each RPC gets its own stream ID on that single TCP connection. All streams travel simultaneously on the same TCP pipe, interleaved at the frame level.

```python
# One subchannel = one TCP = one HTTP/2 connection
# That single TCP can carry many concurrent RPCs as separate streams

stub.GetUser(req1)    # → stream ID 1  ┐
stub.GetUser(req2)    # → stream ID 3  │ all on same TCP connection
stub.ListOrders(req)  # → stream ID 5  │ simultaneously, no waiting
stub.GetProfile(req)  # → stream ID 7  ┘

# On the wire (inside the 1 TCP connection):
# [HEADERS frame, stream=1] [HEADERS frame, stream=3] [DATA frame, stream=5]
# [DATA frame, stream=1]    [HEADERS frame, stream=7] [DATA frame, stream=3]
# → interleaved freely, server separates by stream ID

# Client always uses odd stream IDs: 1, 3, 5, 7, 9...
# Server uses even stream IDs for server-push (rare in gRPC)
# Stream IDs restart from 1 on each new TCP connection (each subchannel)
```

> **HTTP/2 `MAX_CONCURRENT_STREAMS` — not a single fixed number**
> The server advertises a max concurrent streams limit during the HTTP/2 handshake. **100 is a useful mental baseline** but the actual value varies significantly by implementation:
> - **Envoy proxy / AWS ALB** → typically 100 (this is where the "100" number comes from)
> - **Go gRPC server** → defaults to effectively unlimited (`math.MaxUint32`)
> - **Python gRPC server** → constrained by `ThreadPoolExecutor` worker count, not a protocol limit
> - **Java gRPC server** → configurable, defaults to 0 (unlimited)
>
> If your client opens more streams than the server allows, gRPC queues the excess until one finishes. In practice this limit is most relevant when routing through an Envoy proxy or cloud load balancer — not when connecting directly to a language-native gRPC server.

| HTTP/1.1 (REST) | HTTP/2 (gRPC) |
|---|---|
| 1 request per TCP at a time | Unlimited concurrent streams per TCP |
| Must wait for response before next | No waiting — all streams simultaneous |
| 100 concurrent requests = 100 TCP connections | 100 concurrent RPCs = 1 TCP connection |
| High memory, connection overhead | Low memory, connection reuse |

---

## 5. Stub and Interceptors

### 5.1 Stub — The Generated Client Object

The stub is the generated client-side object created from your channel. It has one method per RPC defined in your `.proto` file. Calling `stub.GetUser()` looks like a local function call — internally it serializes your request, picks a subchannel, sends over HTTP/2, and deserializes the response.

```python
stub = UserServiceStub(channel)   # created once, reused for all RPCs

# The stub has NO fixed subchannel assigned to it
# Every RPC call → load balancer Picker decides subchannel at that moment
response1 = stub.GetUser(UserRequest(id=1))    # pick_first: subchannel A
response2 = stub.GetUser(UserRequest(id=2))    # pick_first: subchannel A (same)
response3 = stub.GetOrder(OrderRequest(id=9))  # pick_first: subchannel A (same)

# With round_robin and 3 backends:
response1 = stub.GetUser(req)    # → subchannel A (TCP-A, stream 1)
response2 = stub.GetUser(req)    # → subchannel B (TCP-B, stream 1)
response3 = stub.GetUser(req)    # → subchannel C (TCP-C, stream 1)
response4 = stub.GetUser(req)    # → subchannel A (TCP-A, stream 3)  ← rotates

# Once an RPC is assigned to a subchannel, it stays there until completion
# A long-running streaming RPC never jumps mid-flight to a different subchannel
```

---

### 5.2 Interceptors — Middleware for Every RPC

Interceptors are middleware functions that run before and after every RPC on both client and server. They are independent of your business logic and apply automatically to all RPCs. Think of them as **onion layers** — outermost runs first before, last after.

#### Exact execution order

```
# CLIENT SIDE — request path (outbound):
App code calls stub.GetUser(req)
  → Client Interceptor 1 BEFORE  (e.g. add auth token to metadata)
    → Client Interceptor 2 BEFORE  (e.g. start timer, log request)
      → Protobuf serialization: object → binary
        → HTTP/2 frames built + metadata/deadline added as headers
          → TCP sends binary over network

# CLIENT SIDE — response path (inbound):
          TCP receives response binary
        → Protobuf deserialization: binary → object
      → Client Interceptor 2 AFTER  (e.g. stop timer, log response)
    → Client Interceptor 1 AFTER  (e.g. record metrics)
  → App code receives UserResponse object

# SERVER SIDE — request path (inbound):
TCP receives binary → deserialize → UserRequest object
  → Server Interceptor 1 BEFORE  (e.g. validate auth token)
    → Server Interceptor 2 BEFORE  (e.g. rate limit check)
      → Your handler: GetUser(request, context) runs
      → Handler returns UserResponse
    → Server Interceptor 2 AFTER  (e.g. log response status)
  → Server Interceptor 1 AFTER  (e.g. record server metrics)
→ Serialize response → send binary back over TCP
```

#### Interceptors can abort the chain — auth example

```python
def auth_interceptor(request, context, handler):
    token = dict(context.invocation_metadata()).get('authorization')
    if not token or not validate_token(token):
        context.abort(grpc.StatusCode.UNAUTHENTICATED, 'invalid token')
        return   # chain stops here — interceptor 2 and handler NEVER run
    return handler(request, context)   # pass to next interceptor or handler

# If interceptor 1 aborts: interceptor 2 skipped, handler skipped
# Error response sent immediately back to client
```

#### Interceptor order matters — practical example

```python
# Order 1: [logging, auth]
# logging runs first → logs ALL requests including unauthenticated ones
# auth runs second   → rejects bad tokens after logging
# Use when: you want full visibility into all incoming traffic

# Order 2: [auth, logging]
# auth runs first    → rejects bad tokens immediately, no further processing
# logging runs second → only sees authenticated requests
# Use when: you want clean logs without noise from bad requests
```

#### Common interceptor uses

| Use case | Client side | Server side |
|---|---|---|
| Authentication | Add Bearer token to metadata | Validate token, abort if invalid |
| Logging | Log outgoing request + latency | Log incoming request + status |
| Metrics | Record call count, duration | Record server processing time |
| Tracing | Inject trace ID into metadata | Extract trace ID, create span |
| Rate limiting | Client-side throttle | Reject if rate exceeded |
| Retry logic | Custom retry on specific errors | N/A (server doesn't retry itself) |
| Caching | Return cached response | N/A |

---

## 6. Deadline, Cancellation, Retry, Termination

### 6.1 Deadline — Maximum Wait Time

A deadline is a point in time by which an RPC must complete. If the server has not responded by then, gRPC cancels the call and returns `DEADLINE_EXCEEDED` to the client. Without a deadline, a slow or dead server can hang your client thread forever.

```python
# WITHOUT deadline — dangerous
response = stub.GetUser(UserRequest(id=42))
# if server is slow or dead → this hangs forever → thread stuck → system degrades

# WITH deadline — safe
response = stub.GetUser(UserRequest(id=42), timeout=2.0)  # 2 second max
# after 2s → DEADLINE_EXCEEDED raised → thread freed → handle error gracefully

# Deadline propagation across microservice chain:
# Client → Service A (5s remaining)
#        → Service B (4.8s remaining — A used 0.2s)
#          → Service C (4.5s remaining — B used 0.3s)
# If client deadline expires → DEADLINE_EXCEEDED propagates through entire chain
# → A, B, C all stop work → no wasted CPU anywhere

# Best practice: ALWAYS set a deadline on every RPC. No exceptions.
```

> **Why deadline prevents cascading failure**
> Without deadlines: 1 slow DB on Service C hangs C, which hangs B, which hangs A,
> which hangs all client threads → entire system freezes under load.
> With deadlines: client gives up after 2s, thread freed, error handled gracefully.

---

### 6.2 Cancellation — Stop Right Now

Cancellation is an explicit, immediate stop signal. Different from deadline (time-based auto-stop), cancellation is triggered manually — by your code — when you decide the result is no longer needed. Without it, the server keeps burning CPU and DB resources on work nobody wants.

```python
# Scenario: user types in search box, triggers RPC
# user keeps typing → previous search result is now irrelevant

call = stub.Search.future(SearchRequest(query='py'))  # async call
# user typed more characters...
call.cancel()  # stop immediately — signal sent to server

# Server MUST cooperate — gRPC does not interrupt handler automatically
def Search(self, request, context):
    for item in expensive_db_scan():          # long-running loop
        if not context.is_active():           # check cancellation each iteration
            return SearchResponse()           # stop early, free DB resources
        results.append(process(item))
    return SearchResponse(results=results)

# Cancellation in microservice chain — propagate downstream:
# Client cancels → Service A gets CANCELLED → Service A should cancel its
# call to Service B → Service B cancels its call to Service C
# → entire chain stops work, all resources freed
```

| Deadline | Cancellation |
|---|---|
| Time-based, automatic | Manual, explicit |
| Set at RPC start | Triggered anytime during RPC |
| Server receives remaining time | Server receives cancel signal |
| Example: give up after 2 seconds | Example: user clicked Cancel button |
| Protects against slow/dead servers | Stops unnecessary server work |

---

### 6.3 Retry — Automatic Recovery from Transient Failures

Retry makes gRPC automatically re-attempt a failed RPC without your application knowing about it. Networks blip. Pods restart. Servers have momentary hiccups. Without retry, these transient failures become visible errors. With retry, gRPC silently retries and the user never sees the failure.

```python
# Configure retry policy in service config (not in business logic code)
import json
service_config = json.dumps({
    'methodConfig': [{
        'name': [{'service': 'UserService'}],
        'retryPolicy': {
            'maxAttempts': 4,           # try up to 4 times total
            'initialBackoff': '0.1s',   # wait 0.1s before retry 1
            'maxBackoff': '1s',          # never wait more than 1s
            'backoffMultiplier': 2,      # 0.1s → 0.2s → 0.4s → 0.8s
            'retryableStatusCodes': ['UNAVAILABLE']  # only retry these
        }
    }]
})
channel = grpc.insecure_channel('user:50051',
    options=[('grpc.service_config', service_config)])

# What happens internally:
# attempt 1 → UNAVAILABLE → wait 0.1s
# attempt 2 → UNAVAILABLE → wait 0.2s
# attempt 3 → OK → return response to app code
# App code never saw the 2 failures — completely transparent

# RETRY these (transient, idempotent safe):
#   UNAVAILABLE       → server temporarily down, pod restarting
#   DEADLINE_EXCEEDED → timed out (only if operation is idempotent)

# NEVER retry these (permanent errors — retrying wastes time):
#   INVALID_ARGUMENT  → bad request data, retry won't fix it
#   NOT_FOUND         → resource doesn't exist
#   ALREADY_EXISTS    → duplicate, retry creates another duplicate
#   PERMISSION_DENIED → auth failure, retry won't change permissions

# WARNING — idempotency: only retry operations safe to run multiple times
# GetUser    — safe (same result every time)
# CreateOrder — DANGEROUS (retry might create duplicate orders)
# Use idempotency keys for non-idempotent writes if you need retry

# Transparent retry boundary — when gRPC retries without your config:
# bytes never left client    → unlimited transparent retries (always safe)
# bytes left, server not yet processed → 1 transparent retry (still safe)
# bytes left AND server processed it   → NO automatic retry
#   gRPC cannot know if the server had side effects — it stops here
#   configuring retryableStatusCodes opts YOU into retry responsibility
```

---

### 6.4 Termination — Clean Shutdown

Every channel is a TCP connection. Every server holds a port and threads. If you just kill a process without proper shutdown, TCP connections drop mid-RPC (clients get errors), ports are not released, and file descriptors leak over time.

```python
# SERVER — graceful shutdown (always preferred)
server = grpc.server(ThreadPoolExecutor(max_workers=10))
server.start()

# On SIGTERM / app shutdown signal:
server.stop(grace=30)
# → immediately stop accepting new RPCs
# → wait up to 30 seconds for in-flight RPCs to finish naturally
# → then release port, TCP connections, and thread pool

# SERVER — forceful shutdown (emergency only)
server.stop(grace=None)
# → cancel ALL RPCs immediately including in-flight ones
# → clients receive CANCELLED status
# → use only when graceful shutdown is hanging too long

# CLIENT — always close channel on app shutdown
channel.close()   # release TCP subchannel connections, free threads

# What happens WITHOUT proper termination:
# No server.stop()   → port 50051 stays bound → restart fails 'address in use'
# No channel.close() → TCP stays open on server → zombie connections pile up
# 100 client pods × skipping close = 100 zombie TCP connections on server
# server eventually runs out of file descriptors → crashes

# Kubernetes rolling deploy scenario — why graceful matters:
# k8s sends SIGTERM to old pod → server.stop(grace=10) → 10s to finish RPCs
# without this: every in-flight RPC at deploy time gets hard TCP reset → user errors
```

---

## 7. Complete Request/Response Lifecycle

This section shows exactly what happens for a single `stub.GetUser(req)` call — every step from app code to wire and back — with all concepts working together: channel, name resolution, load balancer, subchannels, TCP, HTTP/2, interceptors, deadline, and the response path.

**Scenario:** 2 clients, 3 backend servers, `round_robin` load balancing, 2 client interceptors, 2 server interceptors, 2-second deadline.

---

### Setup phase — happens once at app start, not per RPC

**Step A — Create channel (no TCP yet)**
```python
channel = grpc.insecure_channel('userservice:50051')
# State: IDLE — no connections, no subchannels, nothing on network
stub = UserServiceStub(channel)  # generated code, wraps channel
```

**Step B — Name resolution — triggered by first RPC**
```
gRPC asks DNS: userservice → [10.0.0.1, 10.0.0.2, 10.0.0.3]
Returns 3 IPs (3 Kubernetes pods) + service config
Runs once per channel lifetime, not per RPC
```

**Step C — Load balancer creates subchannels — 3 TCP connections**
```
round_robin sees 3 IPs → creates 3 subchannels:
  Subchannel A → TCP handshake + HTTP/2 handshake → 10.0.0.1:50051
  Subchannel B → TCP handshake + HTTP/2 handshake → 10.0.0.2:50051
  Subchannel C → TCP handshake + HTTP/2 handshake → 10.0.0.3:50051
All 3 TCPs now open and kept alive (HTTP/2 keepalive pings)
State: READY — channel is ready to serve RPCs
```

> **Production warning — configure keepalives explicitly**
> gRPC does not enable HTTP/2 keepalive pings aggressively enough by default to prevent silent TCP drops by firewalls, AWS ALBs/NLBs, or cloud load balancers. If a subchannel sits idle, an intermediate network device can silently drop the TCP connection without sending a `FIN` or `RST` packet. The client still sees the subchannel as `READY`, sends an RPC, and hangs until the OS TCP timeout fires (which can take minutes). Always configure keepalives on your channel in production:
> ```python
> channel = grpc.insecure_channel('userservice:50051', options=[
>     ('grpc.keepalive_time_ms', 10000),       # send ping every 10s if idle
>     ('grpc.keepalive_timeout_ms', 5000),     # wait 5s for ping ack before closing
>     ('grpc.keepalive_permit_without_calls', True),  # ping even with no active RPCs
> ])
> ```
> Without this, silent TCP drops by firewalls cause mysterious hanging RPCs that only surface under low-traffic conditions — the hardest class of production bug to diagnose.

---

### Request phase — every RPC call

**Step 1 — App calls `stub.GetUser(req, timeout=2.0)`**
```python
response = stub.GetUser(UserRequest(id=42), timeout=2.0)
# Deadline calculated: now + 2.0s = absolute time t_deadline
# This looks like a local function call — all complexity is hidden below
```

**Step 2 — Client Interceptor 1 BEFORE — e.g. auth token**
```
First interceptor runs before anything goes on the wire
Reads token from context, adds to metadata:
  metadata = [('authorization', 'Bearer eyJhbGc...')]
Calls next interceptor in chain
```

**Step 3 — Client Interceptor 2 BEFORE — e.g. logging + tracing**
```
Second interceptor runs: logs outgoing request, starts timer
Injects trace ID into metadata: ('x-trace-id', 'abc-123')
Calls into gRPC runtime to proceed
```

**Step 4 — Serialization — object to binary**
```
gRPC runtime serializes UserRequest(id=42) → protobuf binary
Compact binary — typically 2-5 bytes for a simple int field
No JSON, no text — pure binary encoding from generated pb2 code
```

**Step 5 — Load balancer Picker — which subchannel?**
```
round_robin Picker is consulted for THIS specific RPC
Decision is per-RPC, not per stub or per channel
RPC #1 → Picker returns Subchannel A (10.0.0.1)
RPC #2 → Subchannel B,  RPC #3 → Subchannel C,  RPC #4 → back to A
```

**Step 6 — HTTP/2 stream opened on Subchannel A's TCP connection**
```
Subchannel A already has open TCP connection to 10.0.0.1:50051
NO new TCP handshake — connection is reused
This RPC gets assigned stream ID 1 (or next odd number if others in flight)
Other concurrent RPCs on same TCP get stream IDs 3, 5, 7... — no waiting
```

**Step 7 — HTTP/2 HEADERS frame sent — includes deadline + metadata**
```
HEADERS frame built and sent on stream 1:
  :method            = POST
  :path              = /UserService/GetUser
  content-type       = application/grpc
  grpc-timeout       = 2000m  (deadline as duration)
  authorization      = Bearer eyJhbGc...
  x-trace-id         = abc-123
DATA frame follows containing the protobuf binary body
```

**Step 8 — HTTP/2 frames travel over TCP to server at 10.0.0.1**
```
Frames are binary — not text
If other RPCs are in flight on same TCP, their frames interleave freely:
  [HDR stream=1] [HDR stream=3] [DATA stream=5] [DATA stream=1] [HDR stream=7]
Server reads each frame's stream ID and routes to correct handler
```

---

### Server-side processing

**Step 9 — Server transport receives frames**
```
TCP receives frames on the server side
HTTP/2 layer reassembles frames by stream ID into complete message
Reads grpc-timeout header → knows it has max 2s to respond
Deserializes binary → UserRequest(id=42) object
```

**Step 10 — Server Interceptor 1 BEFORE — e.g. auth validation**
```python
# Reads 'authorization' header from metadata
# Validates token: valid? continue. invalid? abort immediately:
context.abort(grpc.StatusCode.UNAUTHENTICATED, 'bad token')
# → error sent back, handler skipped
# If valid: calls next interceptor
```

**Step 11 — Server Interceptor 2 BEFORE — e.g. rate limit**
```
Checks rate limit for this client IP
If exceeded: abort with RESOURCE_EXHAUSTED
If OK: calls into your handler
```

**Step 12 — Your handler runs — `GetUser(request, context)`**
```python
def GetUser(self, request, context):
    # your business logic — query DB, process data
    user = db.get_user(request.id)
    return UserResponse(id=user.id, name=user.name, email=user.email)

# Handler should periodically check context.is_active() for long operations
# If deadline expires mid-handler: context becomes inactive → return early
```

---

### Response phase

**Step 13 — Server serializes response + interceptors run after**
```
UserResponse(name='Alice') serialized → binary
Server Interceptor 2 AFTER: log response status
Server Interceptor 1 AFTER: record server-side metrics
HTTP/2 DATA frame built with response binary
HTTP/2 HEADERS frame with grpc-status=0 (OK) and trailers sent
```

**Step 14 — Response frames travel back over same TCP subchannel**
```
Response frames travel on stream ID 1 of Subchannel A's TCP
Other RPC responses on streams 3, 5, 7 interleave freely — no blocking
Client transport receives frames, reassembles stream 1 into complete response
```

**Step 15 — Client deserialization + interceptors run after**
```
Binary deserialized → UserResponse(id=1, name='Alice', email='alice@x.com')
Client Interceptor 2 AFTER: stop timer, log total latency
Client Interceptor 1 AFTER: record client-side metrics, push to Prometheus
```

**Step 16 — App receives response**
```python
response.name   # → 'Alice'
response.email  # → 'alice@x.com'

# Your code only saw step 1 and step 16.
# Everything else — name resolution, TCP, HTTP/2, interceptors — was invisible.
```

---

### What happens if deadline expires before step 16?

```python
# At t=2.0 seconds, gRPC checks deadline on both sides:

# Client side:
# → DEADLINE_EXCEEDED raised at stub.GetUser() call site
# → client interceptors AFTER still run (for logging/metrics)
# → TCP stream is reset (RST_STREAM frame sent to server)

# Server side:
# → receives RST_STREAM or detects deadline exceeded
# → context.is_active() returns False
# → if handler checks: it stops early and returns
# → if handler doesn't check: it keeps running (wasting resources)
# → server interceptors AFTER still run

# Why deadline MUST be propagated to downstream calls:
remaining = context.time_remaining()   # how much time is left
payment_response = payment_stub.Charge(req, timeout=remaining)
# → if client deadline already expired, this immediately returns DEADLINE_EXCEEDED
```

### What if the server is temporarily down — retry kicks in

```python
# Step 5 picks Subchannel B. But Server B just restarted — UNAVAILABLE

# gRPC retry logic:
# attempt 1 → Subchannel B → UNAVAILABLE → is UNAVAILABLE retryable? yes
#           → wait initialBackoff (0.1s)
# attempt 2 → Subchannel B (or C with retry-on-next) → OK
#           → return response to app code as if nothing happened

# App code never saw the UNAVAILABLE error
# Once server sends response header → no more retries for that call

# Transparent retry — the wire boundary rule:
#
# Case 1: request never left the client (e.g. TCP dropped before write)
#   → gRPC retries UNLIMITED times transparently, even for non-idempotent ops
#   → safe because bytes never touched the server — no duplicate processing risk
#
# Case 2: request left the client but server never processed it
# (bytes were on wire but server didn't execute handler)
#   → gRPC allows 1 transparent retry
#   → still safe — server saw no effect
#
# Case 3: request left client AND server processed it (handler ran)
#   → gRPC will NOT transparently retry
#   → for non-idempotent ops (CreateUser, CreateOrder): retrying risks duplicate execution
#   → gRPC only retries if the status code is EXPLICITLY listed in your retryPolicy config
#   → if you add UNAVAILABLE to retryableStatusCodes for CreateOrder, YOU are responsible
#      for ensuring idempotency (e.g. via idempotency keys on the server side)
#
# Rule: gRPC is conservative — it only retries beyond Case 2 when you explicitly opt in
# and only for the status codes you list as safe to retry
```

---

## 8. Complete Mental Model

```
══════════════════════════════════════════════════════════════════════
BUILD TIME (once):  .proto → protoc → stub + servicer in your language
══════════════════════════════════════════════════════════════════════

APP START (once per service):
  channel created  →  name resolver  →  [IP1, IP2, IP3]
                                              ↓
                         load balancer  →  subchannel A (TCP → IP1)
                                        →  subchannel B (TCP → IP2)
                                        →  subchannel C (TCP → IP3)

══════════════════════════════════════════════════════════════════════
PER RPC (every call):
══════════════════════════════════════════════════════════════════════

App code                                               Server handler
   │                                                        │
   ↓  stub.GetUser(req, timeout=2s)                         │
   │                                                        │
   ↓  [Client Interceptor 1 BEFORE] auth token              │
   ↓  [Client Interceptor 2 BEFORE] log, trace              │
   │                                                        │
   ↓  serialize → binary                                    │
   │                                                        │
   ↓  LB Picker → subchannel A                              │
   │              (TCP already open, reused)                │
   │                                                        │
   ↓  HTTP/2 stream opened (stream ID 1)                    │
   ↓  HEADERS frame: method, path, deadline, metadata       │
   ↓  DATA frame: protobuf binary                           │
   │                                                        │
   └──────────── binary frames over TCP ───────────────────►│
                                                            │
                                               deserialize → object
                                                            │
                                 [Server Interceptor 1 BEFORE] auth
                                 [Server Interceptor 2 BEFORE] rate limit
                                                            │
                                          GetUser(request, context)
                                               DB query, process
                                          return UserResponse
                                                            │
                                 [Server Interceptor 2 AFTER]  log
                                 [Server Interceptor 1 AFTER]  metrics
                                                            │
                                          serialize → binary
                                                            │
   ◄──────────── binary frames over TCP ───────────────────┘
   │
   ↓  deserialize → UserResponse object
   │
   ↓  [Client Interceptor 2 AFTER] stop timer, log latency
   ↓  [Client Interceptor 1 AFTER] push metrics
   │
   ↓  App receives: response.name = 'Alice'

══════════════════════════════════════════════════════════════════════
TCP / HTTP/2 PICTURE:
══════════════════════════════════════════════════════════════════════

Client A ──── 1 TCP (subchannel A) ──── Server pod 1
              stream 1 = GetUser(1)   ┐  all on same TCP
              stream 3 = GetUser(7)   │  simultaneously
              stream 5 = ListOrders() ┘  no waiting

Client B ──── 1 TCP (subchannel B) ──── Server pod 2
              stream 1 = GetProfile() ┐  separate TCP
              stream 3 = CreateUser() ┘  own stream ID space

N clients × M backend servers = N × M TCP connections total
Each TCP carries unlimited concurrent RPCs as HTTP/2 streams
```

---

## 9. Quick Reference

### Concepts at a glance

| Concept | What it is | Created when | Count |
|---|---|---|---|
| **Channel** | Config object, address + credentials | Once at app start | 1 per target service |
| **Subchannel** | 1 TCP connection to 1 IP:port | On first RPC (lazy) | 1 per resolved IP (policy decides) |
| **TCP connection** | Real network socket | Same time as subchannel | Same as subchannels |
| **HTTP/2 stream** | 1 RPC's virtual lane inside TCP | Per RPC call | Unlimited per TCP (default max 100) |
| **Stub** | Generated client object | After channel created | 1 per service, reused |
| **Name resolver** | DNS / service discovery | Once per channel | 1 per channel |
| **Load balancer** | Subchannel manager + RPC picker | Once per channel | 1 per channel |
| **Interceptor** | Middleware, runs per RPC | Every RPC (both sides) | Runs N times = N interceptors |

### Resilience features

| Concept | Why you need it | Best practice |
|---|---|---|
| **Deadline** | Prevent infinite hang on slow server | ALWAYS set. Every single RPC. |
| **Cancellation** | Stop server work when result unwanted | Check `context.is_active()` in long handlers |
| **Retry** | Survive transient network / pod failures | Only for idempotent ops + retriable status codes |
| **Termination** | Release TCP, port, threads cleanly | Always `stop(grace=N)` on SIGTERM |
| **Keepalive** | Prevent silent TCP drops by firewalls/ALBs | Always set `keepalive_time_ms` on channel in production |

### Load balancer policy decision

| LB Policy | Subchannels | RPC routing | Requires xDS? | Use when |
|---|---|---|---|---|
| `pick_first` | 1 (tries IPs sequentially, locks on first success) | All RPCs → same TCP | No | 1 server, or connection-time failover |
| `round_robin` | 1 per IP | Rotates per RPC | No | Multiple backends, even load |
| `weighted_round_robin` | 1 per IP | More to faster backends | Yes — needs control plane | Mixed server capacity |
| proxy / k8s ClusterIP | 1 (to proxy) | Proxy decides | No | k8s Service, Envoy, Istio |

---
