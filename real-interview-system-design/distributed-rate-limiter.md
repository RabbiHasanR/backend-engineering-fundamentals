# Distributed Rate Limiter — Complete System Design

---

## What Is a Rate Limiter?

A rate limiter controls how many requests a client can make within a specific time window. Think of a social media app where a user can view their feed, post updates, or search — the rate limiter caps them at, say, **100 requests per minute**. Without it, a bad actor could spam thousands of requests and bring down backend services for everyone else.

**Core purpose:** Protect backend infrastructure from abuse, overload, and denial-of-service scenarios.

---

## Step 1: Requirements

### Functional Requirements

These are the *features* the system must deliver, in order of execution when a request arrives:

1. **Identify clients** — Know *who* is making the request (User ID, IP address, or API key).
2. **Limit requests based on configurable rules** — e.g., "100 requests per minute per user" or "1000 requests per minute for premium users."
3. **Return proper error codes and headers** — Tell the client *why* they were rejected and what they can do next.

### Scale (clarified with interviewer)

- **100 million** daily active users
- **1 million requests per second** at peak

### Non-Functional Requirements

| Quality | Specifics |
|---|---|
| **Availability over Consistency** | Rate limiter must stay up even if rules are briefly stale. Prefer eventual consistency (CAP theorem: A over C). |
| **Low Latency** | Rate limit checks must add **< 10ms** to every request. |
| **Scalability** | Must handle **1 million requests/second** reliably. |

> **Why availability over consistency?** If a new rule is being pushed (e.g., reducing a user's limit from 200 to 100), we'd rather the rate limiter continue working with the old rule for a few seconds than go offline waiting for the rule to fully propagate everywhere.

---

## Step 2: Core Entities

| Entity | Description |
|---|---|
| **Request** | The incoming HTTP call — carries headers, IP, auth tokens |
| **Client** | The identity making the request: User ID, IP address, or API key |
| **Rule** | The limit definition: `{ clientType: "premium", limit: 1000, windowSeconds: 60 }` |

---

## Step 3: System Interface

The rate limiter exposes a single internal function (not a public API — this is called by the gateway via RPC):

```
isRequestAllowed(clientId: string, rule: Rule) → {
  allowed: boolean,
  remainingTokens: int,
  resetAt: timestamp
}
```

This is the contract everything else is built around.

---

## Step 4: High-Level Design

### 4a. Where Should the Rate Limiter Live?

Three placement options to consider:

#### Option A — Inside Each Microservice
Each service checks its own local memory.

```
Client → Gateway → [Microservice A (local RL)] → DB
                 → [Microservice B (local RL)] → DB
```

❌ **Problem:** No global picture. If Alice hits Service A and Service B, each thinks she's only made 1 request — but globally she made 2. No coordination.

---

#### Option B — Standalone Rate Limiter Service
A dedicated service called by every microservice.

```
Client → Gateway → Microservice → Rate Limiter Service → Redis
```

❌ **Problem:** Every request now makes two hops (microservice → rate limiter → back). Adds unnecessary network latency.

---

#### Option C — At the API Gateway Edge ✅ (Chosen)
The rate limiter sits at the very front of the system.

```
Client → [API Gateway + Rate Limiter] → Microservice A
                                      → Microservice B
```

✅ **Benefits:**
- Requests are blocked *before* they hit any service ("bouncer at the door")
- No extra network hop inside the system
- Microservices stay clean — zero rate-limiting logic

> **Limitation to acknowledge:** The gateway only sees what's in the HTTP request (headers, IP, URL, JWT tokens). It can't reach into your database for complex business logic. Handle this by encoding user tier (e.g., `premium: true`) in the JWT token.

---

### 4b. How to Identify Clients

| Identifier | Best For |
|---|---|
| **User ID** | Authenticated users with accounts |
| **IP Address** | Anonymous/unauthenticated users |
| **API Key** | Developer APIs and B2B integrations |

In production you combine these in layers:

```
Alice (authenticated) → 1000 req/min
Anonymous IP 1.2.3.4  → 100 req/min
API Key xyz123        → 50,000 req/min
```

The right identifier is read directly from the request headers or JWT.

---

### 4c. Rate Limiting Algorithms

Here are the four main algorithms, from simplest to most production-ready:

---

#### Algorithm 1: Fixed Window Counter

Each user gets `N` requests per time window (e.g., 100 requests/minute). A counter resets at the top of each window.

```
Window: 12:00 → 12:01
Alice counter: 0 → 1 → 2 → ... → 100 → REJECT
Counter resets at 12:01 → 0
```

**Storage:** Hash map of `clientId → { count, windowStart }`

```
{ "alice": { count: 100, windowStart: "12:00" },
  "bob":   { count: 5,   windowStart: "12:00" } }
```

✅ Simple to implement  
❌ **Boundary burst problem:** Alice can make 100 requests at 12:00:59 and 100 more at 12:01:01 — that's 200 requests in 2 seconds.  
❌ Starvation: If you use all 100 at 12:00:01, you wait 59 seconds.

---

#### Algorithm 2: Sliding Window Log

Track the exact timestamp of every request. Count requests in the rolling last-60-seconds window.

```
Now: 12:01:30
Requests in last 60s: [12:00:31, 12:00:45, 12:01:10, 12:01:25] → count=4
```

✅ Perfect accuracy, no boundary effects  
❌ High memory — must store every timestamp per user (heap/deque data structure). At scale with millions of users, this is very expensive.

---

#### Algorithm 3: Sliding Window Counter

A memory-efficient approximation of the sliding window. Track two counters: the **previous full window** and the **current window**, then estimate.

**Example:**
```
Previous window (12:00–12:01): 8 requests
Current window (12:01–12:02): 6 requests, 42 seconds in (70% through)

Estimated count = currentRequests + (1 - 0.70) × previousRequests
               = 6 + 0.30 × 8
               = 6 + 2.4
               = 8.4

Limit = 10 → 8.4 < 10 → ALLOW ✅
```

✅ Much less memory (just 2 integers per user)  
❌ Approximation — assumes requests are evenly distributed, which isn't always true

---

#### Algorithm 4: Token Bucket ✅ (Chosen)

Each client has a bucket with a **burst capacity** (max tokens). Tokens refill at a steady **refill rate**. Each request consumes one token. If the bucket is empty → reject.

```
Bucket capacity: 100 tokens  (max burst)
Refill rate:     10 tokens/min  (steady throughput)

Alice at 12:00: bucket = 100
Alice makes 100 requests: bucket = 0
Alice at 12:01: bucket = 10 (refilled)
Alice makes 10 requests: bucket = 0
...
```

**State stored per user:** just `{ tokenCount, lastRefillTimestamp }` — only 2 values.

✅ Handles bursts gracefully (bucket size = burst capacity)  
✅ Enforces steady-state throughput (refill rate)  
✅ Minimal memory — 2 integers per user  
✅ Widely used in production (AWS API Gateway, Stripe, etc.)

---

### 4d. Storing State: Redis

The token bucket state (`tokenCount`, `lastRefillTimestamp`) must be **shared across all gateway instances**. If each gateway kept its own local state, the same problem as Option A returns.

**Solution: Redis (in-memory cache)**

```
[Gateway A] ──┐
              ├──→ [Redis] { "alice": { tokens: 50, lastRefill: 1700000000 } }
[Gateway B] ──┘
```

**Request flow step-by-step:**

```
1. Request arrives at Gateway
2. Gateway fetches Alice's bucket from Redis:
      HMGET alice tokens lastRefill
3. Calculate tokens to add since lastRefill:
      elapsed = now - lastRefill = 30 seconds
      tokensToAdd = elapsed × refillRate = 30 × 1 = 30
      newCount = storedCount + tokensToAdd = 20 + 30 = 50
4. Check: newCount > 0?
      YES → ALLOW the request
5. Write updated state back to Redis:
      HMSET alice tokens 49 lastRefill <now>
```

---

### 4e. Returning Proper Error Codes and Headers

When a request is **rejected**, return:

```
HTTP 429 Too Many Requests

Headers:
  X-RateLimit-Limit: 100          ← total limit per window
  X-RateLimit-Remaining: 0        ← tokens left
  X-RateLimit-Reset: 1700000060   ← Unix timestamp when it resets
  Retry-After: 45                 ← seconds until retry is safe
```

**Why fail fast (reject immediately) rather than queue?**

If a user requests their feed and we queue the request, they wait and wait and think it's broken — then hit the button again. Now we have a backlog growing with duplicate requests. Fail fast is always correct for interactive, user-facing APIs. Queuing only makes sense for async batch processing systems.

---

## Step 5: Deep Dives (Non-Functional Requirements)

### Deep Dive 1: Scalability (1M req/sec)

**Problem:** A single Redis instance handles ~100,000 ops/sec. Each rate limit check needs 2 Redis ops (HMGET + HMSET), so one Redis instance supports only ~50,000 req/sec. We need 1,000,000 — that's 20× too slow.

**Solution: Redis Sharding**

Shard user data across multiple Redis instances. Each user's bucket lives on exactly one shard, determined by their client ID.

```
Shards needed = 1,000,000 req/sec ÷ 50,000 ops/sec = 20 shards minimum
(Add headroom → provision 25–30 shards)
```

```
clientId hash → Shard assignment

alice  → Redis Shard 3
bob    → Redis Shard 11
carol  → Redis Shard 7
```

**How to shard in practice:** Use **Redis Cluster**, which automatically manages sharding using ~16,000 hash slots distributed across nodes. The gateway's Redis client (e.g., redis-py, ioredis) handles routing transparently — you just configure the cluster endpoint.

---

### Deep Dive 2: Availability & Fault Tolerance

**What happens if a Redis shard goes down?**

Two failure modes to discuss with your interviewer:

| Mode | Behavior | Risk |
|---|---|---|
| **Fail Open** | Rate limiter is down → all requests pass through | Downstream services get hammered; cascading failures possible |
| **Fail Close** | Rate limiter is down → all requests rejected | Site appears down to users; bad UX |

**Recommended approach:** Fail close by default for a system protecting critical backend services. However, a smarter fallback is:

> Each gateway holds a simple **in-memory fixed window counter** as a local fallback. If Redis is unreachable, fall back to local rate limiting temporarily. It's not perfect (no cross-instance coordination) but it's far better than fully failing open or closed while Redis recovers.

**Solution: Redis Cluster with Read Replicas**

Each shard has 1–2 async replicas. Writes go to the primary; if it fails, a replica is promoted automatically.

```
[Shard 3 Primary] ──async replication──→ [Shard 3 Replica]
       ↑
   Alice's bucket
   
Primary fails → Replica promoted → Reads/writes continue
```

Trade-off: Async replication means a brief window where the replica might not have the latest write. Alice might get one extra request past her limit — acceptable for a social network rate limiter.

---

### Deep Dive 3: Low Latency (< 10ms)

Every request passes through the rate limiter, so latency is critical.

**Optimization 1: Connection Pooling**

Instead of opening a new TCP connection to Redis per request (20–50ms overhead for handshake), maintain a **persistent pool** of connections.

```
Gateway maintains: ConnectionPool(size=50, host=redis-cluster)

Request 1 → borrows connection from pool → sends HMGET/HMSET → returns connection
Request 2 → borrows another connection → ... → returns
```

Most Redis clients (redis-py, ioredis, Jedis) do this automatically. Tune pool size based on your expected concurrent request volume.

**Optimization 2: Geographic Colocation**

Deploy gateways and Redis close to your users:

```
Tokyo users    → Tokyo Gateway + Tokyo Redis  (< 1ms network)
London users   → London Gateway + London Redis (< 1ms network)
```

Keep Redis and the gateway in the **same data center**, ideally the same rack. Network round-trip between co-located servers: ~0.1–0.5ms vs. cross-region: 50–150ms.

---

### Deep Dive 4: Dynamic Rule Configuration

**Problem:** Right now rules are hardcoded. In production you need to change limits without redeploying the gateway (e.g., temporarily raise limits during a product launch, or lower them during an incident).

**Option A: Database polling (❌ Not ideal)**
Gateway polls the DB every N seconds.
- Delay = polling interval (could be 10–30 seconds)
- Wastes CPU on constant polling
- Rules are still slightly stale

**Option B: Read rules from Redis on every check (❌ Not ideal)**
Each rate limit check also reads the current rules.
- Adds extra Redis ops per check
- Rules rarely change — wasteful

**Option C: Push-based configuration with ZooKeeper / etcd ✅**

Store rules in a distributed config store (ZooKeeper or etcd). Gateways:
1. Fetch all rules on startup → cache them **in local memory**
2. Subscribe (open persistent TCP connection) to watch for changes
3. When a rule changes, the config store **pushes** the update over the open connection
4. Gateway updates its in-memory cache instantly

```
[Admin] updates rule → [etcd/ZooKeeper]
                              ↓ push over open TCP connection
                       [Gateway A] (updates in-memory rules)
                       [Gateway B] (updates in-memory rules)
                       [Gateway C] (updates in-memory rules)
```

✅ Zero latency overhead on the hot path (rules are in memory)  
✅ Near-instant propagation when rules change  
✅ No wasted polling CPU

---

### Deep Dive 5: Race Condition in Redis

**Problem:** Two gateways read Alice's token count simultaneously, both see 1 token, both allow the request, both write back `0` — but Alice actually used 2 tokens at once.

```
Gateway A reads: tokens = 1  ──┐
Gateway B reads: tokens = 1  ──┤  Both read before either writes
                               ↓
Gateway A writes: tokens = 0
Gateway B writes: tokens = 0  ← overwrites A, effective loss of one decrement
```

This is a classic **read-modify-write race condition**.

**Solution: Lua Scripting in Redis**

Redis is single-threaded and supports atomic Lua scripts. A Lua script that does the full read + calculate + write cycle executes atomically — no other command can interrupt it.

```lua
-- Atomic token bucket check (pseudo-Lua)
local key = KEYS[1]
local refillRate = tonumber(ARGV[1])
local capacity = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

local data = redis.call("HMGET", key, "tokens", "lastRefill")
local tokens = tonumber(data[1]) or capacity
local lastRefill = tonumber(data[2]) or now

local elapsed = now - lastRefill
local newTokens = math.min(capacity, tokens + elapsed * refillRate)

if newTokens >= 1 then
  redis.call("HMSET", key, "tokens", newTokens - 1, "lastRefill", now)
  return 1  -- allowed
else
  return 0  -- rejected
end
```

The entire read-calculate-write sequence is atomic. Gateway A's script runs to completion before Gateway B's script can start.

---

## Final Architecture Diagram

```
                        ┌─────────────────────────────────┐
                        │         etcd / ZooKeeper         │
                        │   (push-based rule config)       │
                        └──────────────┬──────────────────┘
                                       │ push on change
          ┌────────────────────────────▼──────────────────────────────┐
          │                    API Gateway Layer                       │
          │  ┌─────────────────────────────────────────────────────┐  │
          │  │  Gateway A  │  Gateway B  │  Gateway C              │  │
          │  │  (in-memory rules cache)                            │  │
          │  └──────────────────────────┬──────────────────────────┘  │
          └─────────────────────────────┼─────────────────────────────┘
                                        │ HMGET/HMSET via Lua script
          ┌─────────────────────────────▼─────────────────────────────┐
          │                  Redis Cluster (Sharded)                   │
          │  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
          │  │ Shard 1  │  │ Shard 2  │  │ Shard N  │  (20+ shards) │
          │  │ + Replica│  │ + Replica│  │ + Replica│               │
          │  └──────────┘  └──────────┘  └──────────┘               │
          └───────────────────────────────────────────────────────────┘
                                        │
                     ┌──────────────────▼──────────────────┐
                     │          Microservices               │
                     │  [Posts]  [Search]  [Notifications] │
                     └─────────────────────────────────────┘
```

---

## Summary Table

| Decision | Choice | Reason |
|---|---|---|
| Placement | API Gateway (edge) | Blocks bad requests before they reach services |
| Client Identity | User ID + IP + API Key (layered) | Different limits for different client types |
| Algorithm | Token Bucket | Handles bursts + steady rate, minimal memory (2 integers/user) |
| State Storage | Redis Cluster | Sub-millisecond ops, in-memory, supports sharding + replication |
| Sharding | Redis Cluster (hash slots) | Scale to 1M req/sec across 20+ shards |
| Fault Tolerance | Read replicas + local fallback counter | High availability; fail close by default |
| Latency | Connection pooling + geographic colocation | < 10ms target |
| Rule Updates | etcd/ZooKeeper push | Zero hot-path overhead, near-instant propagation |
| Race Condition | Redis Lua scripting | Atomic read-modify-write |
| Rejection Response | HTTP 429 + headers | Standard protocol; client knows when to retry |

---

## What's Expected by Level

### Mid-Level Engineer
- Know the 4 algorithms and justify your choice
- Propose Redis for shared state and explain why
- Handle interviewer probes about single-Redis bottleneck and failure scenarios

### Senior Engineer
- Proactively identify the single-Redis bottleneck and derive the math (50K ops → 20 shards)
- Bring up fail-open vs fail-close trade-offs unprompted
- Discuss connection pooling and geographic distribution

### Staff Engineer
- Drive the entire design proactively
- Deep dive on Redis Cluster internals (hash slots vs consistent hashing)
- Identify and solve the race condition with Lua scripting
- Discuss real-world operational lessons (pool sizing mistakes, cascading failures, etc.)