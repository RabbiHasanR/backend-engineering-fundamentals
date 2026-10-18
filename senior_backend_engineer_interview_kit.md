# Senior Backend Engineer — Interview Kit

Role: 3–5 yrs, Python + PostgreSQL, leads 2–3 engineers.

**Rules:** same core questions for everyone · wait 10–15 s before hinting · "I don't know" → ask "How would you find out?" · score right after the interview.

| Round | Section | Time |
| --- | --- | --- |
| 1 | Fundamentals | 60 min |
| 2 | Existing project | 45 min |
| 3 | Tech choices + system design | 60 min |
| 4 | Debugging & performance | 45 min |
| 5 | Legacy, team & delivery | 30 min |
| 6 | AI & security | 30 min |
| 7 | Coding | 20–30 min |
| 8 | DevOps & AWS | 30 min |

---

## 1. Fundamentals

### Q1. GIL, threads vs asyncio vs processes

**Ask:** What is the GIL? Concurrency vs parallelism? When do you use threads, asyncio, processes?

**Answer:**

- Concurrency = many tasks in progress (interleaved). Parallelism = running at the same instant on multiple cores.
- GIL: one thread runs Python bytecode at a time; released during I/O.
- Threads → I/O-bound work with blocking libraries.
- asyncio → thousands of concurrent I/O connections (APIs, WebSockets); needs async libraries end to end.
- Processes → CPU-bound work; real parallelism, more memory.

**Follow-ups:** FastAPI `def` vs `async def`? (threadpool vs event loop) · `time.sleep()` inside `async def`? (blocks every request on that worker)

**Red flag:** "asyncio makes code faster."

### Q2. Transactions & isolation levels

**Ask:** What is a transaction and why does it matter? What are isolation levels?

**Answer:**

- All-or-nothing unit of work (ACID). Example: money transfer.
- PG levels: **Read Committed** (default), **Repeatable Read** (one snapshot), **Serializable** (as if one by one — app must retry on error `40001`).
- Write skew is still possible under Repeatable Read.
- Keep transactions short: long ones hold locks and block VACUUM.

**Follow-ups:** Example of write skew? (two doctors both go off call) · Send a Celery task after saving — what can go wrong? (`transaction.on_commit` / outbox)

**Red flag:** only knows `@atomic`, can't say what it protects.

### Q3. Logic in DB function/trigger vs app

**Ask:** When should logic live in a PL/pgSQL function or trigger? When is that a mistake?

**Answer:**

- **DB:** integrity rules for every writer (constraints first, then triggers), audit logs, heavy set-based processing.
- **App:** business rules that change often, external calls, anything that needs easy testing and review.
- Triggers are hidden side effects; the DB is the hardest component to scale.

**Follow-ups:** Safe dynamic SQL? (`format()` with `%I`/`%L`, `EXECUTE ... USING`) · Risk of `SECURITY DEFINER`? (set `search_path`)

**Red flag:** "always app" or "always DB".

### Q4. NOT NULL column on a 50M-row table, no downtime

**Ask:** How do you add a NOT NULL column to a 50M-row production table without downtime?

**Answer:**

- Constant default (PG 11+): `ADD COLUMN ... NOT NULL DEFAULT 0` is instant.
- Always `SET lock_timeout` — a waiting ALTER blocks every query queued behind it.
- Computed values: add nullable → app writes it → backfill in batches → `CHECK ... NOT VALID` → `VALIDATE` → `SET NOT NULL` (PG 12+ skips the scan).

**Follow-ups:** Index without blocking writes? (`CREATE INDEX CONCURRENTLY`) · Rename a column safely? (expand/contract)

**Red flag:** one giant `UPDATE` of 50M rows.

### Q5. Caching

**Ask:** When do you cache? Which pattern? How do you invalidate? LRU or LFU?

**Answer:**

- Cache read-heavy, expensive, staleness-tolerant data. Don't cache balances or stock at checkout.
- Cache-aside is the default pattern.
- Invalidate: TTL with jitter, **delete** the key **after** commit.
- LRU = good default. LFU = stable hot set with occasional one-off scans.
- Redis default is `noeviction` — set `maxmemory-policy` for a cache.

**Follow-ups:** A hot key expires and 5k requests hit the DB? (stampede → lock / serve stale) · Redis down — what happens to the DB?

**Red flag:** "cache everything."

### Q6. Two requests update the same row

**Ask:** Two requests update the same row at the same moment — what happens and how do you keep it correct?

**Answer:**

- PG locks the row; the second update waits.
- The real bug is app-level read-modify-write → **lost update**.
- Fixes:
  - Atomic `SET stock = stock - 1 WHERE stock > 0`
  - `SELECT ... FOR UPDATE`
  - Optimistic locking (version column)
  - Serializable + retry

**Follow-ups:** Deadlock? (lock in a consistent order) · Job queue with many workers? (`FOR UPDATE SKIP LOCKED`)

**Red flag:** "Postgres handles it automatically."

### Q7. ORM or raw SQL

**Ask:** When do you use an ORM and when do you write raw SQL?

**Answer:**

- **ORM by default** for CRUD and simple joins:
  - Faster to write
  - Safe parameters by default
  - Migrations, readable code
- **Raw SQL / PL/pgSQL when the ORM gets in the way:**
  - Complex reports, window functions, CTEs
  - Bulk updates and upserts (`INSERT ... ON CONFLICT`)
  - Hot paths where the ORM's generated query is slow
- **Mix them:** ORM for most code, raw SQL in a repository/query layer — always parameterized.
- Know what the ORM generates: log or `EXPLAIN` it; fix N+1 with `select_related` / `prefetch_related`; use `only()` / `values()` for big tables.

**Follow-ups:** How do you spot N+1 in production? (query count per request, `pg_stat_statements`, APM) · Raw SQL with user input — how do you keep it safe? (bind params, never f-strings)

**Red flag:** "ORMs are always slow" or "never write SQL"; can't say what query the ORM produces.

### Q8. Production-grade REST API

**Ask:** How do you design a production-grade REST API?

**Answer:**

- **Resources & methods:** plural nouns (`/matches/{id}/events`), HTTP verbs with correct meaning; GET/PUT/DELETE idempotent.
- **Status codes:** 201 created, 204 no content, 400 bad input, 401 not logged in, 403 not allowed, 404, 409 conflict, 422 validation, 429 rate limited.
- **One error format** everywhere (e.g. RFC 9457 problem details): code, message, field errors, request ID.
- **Pagination:** cursor/keyset for large or changing lists; offset only for small admin lists. Whitelist filter/sort fields.
- **Idempotency-Key** header on POSTs that must not run twice (payments, orders).
- **Security:** validate input (Pydantic), auth (JWT/OAuth2), authorization per object, rate limits, request size limits.
- **Versioning:** additive changes first; `/v2` only for breaking changes; deprecation timeline.
- **Mobile-friendly:** small payloads, gzip, `ETag` / conditional requests.
- **Observability & contract:** request ID, structured logs, metrics, tracing; OpenAPI spec as the contract.

**Follow-ups:** 401 vs 403? · PUT vs PATCH? (replace vs partial update) · Why cursor over offset? (offset gets slow on deep pages and skips/duplicates rows when data changes)

**Red flag:** verbs in URLs (`/getUser`); returns 200 with `{"error": ...}`; no pagination.

### Q9. REST vs GraphQL vs gRPC vs WebSocket

**Ask:** When do you use REST, GraphQL, gRPC, WebSocket or SSE?

**Answer:**

| Protocol | Use when | Watch out for |
| --- | --- | --- |
| **REST** | Default for public, web and mobile APIs; CRUD | Over/under-fetching; many round trips |
| **GraphQL** | Many clients needing different shapes of data; aggregating several services | HTTP caching harder, N+1 (needs DataLoader), query cost limits |
| **gRPC** | Internal service-to-service; low latency; strict protobuf contracts; streaming | Not browser-native (needs grpc-web); binary, harder to debug |
| **WebSocket** | Two-way real-time: chat, live interaction | Stateful connections — scaling, load balancing, reconnects |
| **SSE** | One-way server → client push: live score ticker | Server → client only |
| **Webhooks** | Notifying external systems | Retries, signature verification |

Typical mix: REST outside, gRPC inside where performance matters, WebSocket/SSE for real-time.

**Follow-ups:** Live match scores — WebSocket or SSE? (SSE is enough if clients only receive) · Why not GraphQL for everything?

**Red flag:** "GraphQL/gRPC because it's modern"; can't name a downside of their favourite.

### Q10. Event-driven architecture

**Ask:** What is event-driven architecture? Pros, cons, and when do you use it?

**Answer:**

- Services publish **events** (facts: `OrderPlaced`, `GoalScored`) instead of calling each other; consumers react independently.
- **Pros:** loose coupling, add new consumers without touching the producer, absorbs traffic spikes, replay/audit (Kafka).
- **Cons:** eventual consistency, harder debugging (need tracing), ordering, duplicates, event schema evolution.
- **Must-knows:**
  - Delivery is **at-least-once** → consumers must be **idempotent**
  - **Outbox pattern:** write the event to a DB table in the same transaction, relay publishes it — no lost events
  - Ordering only per key (Kafka partition key, e.g. `match_id`)
  - Dead-letter queue for poison messages; versioned event schemas
  - Choreography (services react to events) vs orchestration (a saga coordinator)
- **Kafka** = durable log, replay, high throughput. **RabbitMQ** = task queues, flexible routing, per-message ack.

**Follow-ups:** DB commit succeeded but the publish failed — how do you prevent it? (outbox) · Same event processed twice? (processed-event table, upserts, idempotency key)

**Red flag:** events for everything, even simple request/response; ignores duplicates and ordering.

### Q11. Async / background tasks

**Ask:** How do you handle async or background tasks?

**Answer:**

- **Move out of the request:** emails, SMS, push, image/video processing, reports, third-party and AI calls.
- **Tools:**
  - FastAPI `BackgroundTasks` → trivial work only (runs in-process, lost if the server dies)
  - Celery / RQ / Dramatiq / arq with Redis or RabbitMQ → most production work
  - PG table + `FOR UPDATE SKIP LOCKED` → small scale, no extra infra
  - Celery beat / cron → scheduled jobs
- **Reliability:**
  - Enqueue **after commit** (`transaction.on_commit` / outbox)
  - **Idempotent** tasks
  - Retries with exponential backoff + jitter, max retries, DLQ
  - Timeouts; `acks_late` so a crashed worker's task is redelivered
  - Pass **IDs**, not objects
- **Client:** return `202 Accepted` + job ID → poll status, webhook, or push.
- **Operate:** separate queues by priority (OTP ≠ reports); monitor queue length, task latency, failure rate.

**Follow-ups:** Worker crashes mid-task? (`acks_late` + idempotent task) · Why pass an ID, not the object? (object goes stale, large payload, pickling)

**Red flag:** payments in `BackgroundTasks`; no retries; tasks not idempotent; sending the task before the commit.

---

## 2. Existing project

Have them **draw** their system. Judge clarity and ownership.

| Ask | Good answer | Red flag |
| --- | --- | --- |
| Walk one request client → DB → response. Where is each piece of state? | Names LB, workers, cache, DB, queue, S3 in order | "Frontend calls backend calls DB" |
| RPS, DB size, p95 latency? | Rough numbers + where to see them | No idea |
| What breaks if Redis / DB / queue / third-party API goes down? | Blast radius, timeouts, fallbacks | "It never goes down" |
| A decision **you** made — what did you reject and why? | Real trade-off, says "I" | Only "we", no alternative |
| Rebuild today — what would you change? | Specific, tied to real pain | "Nothing" or "rewrite in X" |

---

## 3. Tech choices & system design

### Q12. Choosing language, framework and database

**Ask:** For a new service, how do you decide which language, framework and database to use? PostgreSQL or MongoDB?

**Answer:**

- **Start from requirements:**
  - Data shape and access patterns
  - Consistency needs
  - Scale and latency
  - Team skills
  - Operating cost
- **Prefer boring, proven tech** the team already runs. Every new technology adds ops, monitoring and hiring cost.
- **Language/framework:**
  - Python **Django** → admin, CRUD-heavy work, batteries included
  - **FastAPI** → async APIs, high I/O concurrency
  - **Go** → only when there's a real need, e.g. a very high-concurrency WebSocket gateway
- **PostgreSQL by default:**
  - Relational data, transactions, joins
  - JSONB covers semi-structured fields
- **MongoDB when:**
  - Documents are read and written as a whole (aggregates)
  - Schema varies a lot per record
  - Little cross-document transactional logic
  - Need easy horizontal write scaling
- **Alongside the primary DB, not instead of it:**
  - Redis → cache, rate limits, ephemeral state
  - Elasticsearch → full-text search, synced from PG
  - Kafka → event streams and replay; RabbitMQ → task queues and routing
- **Process:** spike or prototype for risky choices; write a short ADR (context, options, decision, consequences). Move fast on reversible decisions, slow on irreversible ones (the database).

**Follow-ups:** When is MongoDB the wrong choice? (financial data, many relations, reporting with joins) · When would you **not** add a new technology even though it fits?

**Red flag:** "Whatever is trending"; "MongoDB because no schema = faster"; ignores team skills and operating cost.

### Q13. System design (pick one)

Expect: clarify requirements → API & data model → components → deep dive → failures, scaling, monitoring, security.

| Design | Key points of a strong answer |
| --- | --- |
| **Live match scores** | Write to PG → publish event (Redis/Kafka) → WebSocket gateways push per match channel; CDN-cached REST snapshot (1–5 s TTL); sequence numbers for reconnect; pre-scale before big matches |
| **Notification service** | Idempotency key → queue → per-channel workers (FCM/APNs/SMS/email); retries with backoff + DLQ; priority queues (OTP before marketing); user preferences & rate limits; topic fan-out for millions |
| **Face verification** | Liveness check → pre-signed S3 upload → async GPU worker → embedding similarity vs threshold → manual review for borderline; model versioning; encrypt biometrics, audit access, retention policy |

#### Constraint twists

| Twist | Strong answer |
| --- | --- |
| 10× traffic on match day | Pre-scale, CDN, coalesce updates, load shedding, protect DB (cache, replicas, PgBouncer) |
| Slow 3G / offline mobile | Small delta payloads, snapshot + sequence numbers, backoff + jitter on reconnect, push when backgrounded, client-generated IDs for idempotency |
| Redis died | Pub/sub messages lost, DB load spike → circuit breaker; managed Redis with failover; Streams/Kafka where durability matters |
| Breaking API change, old app versions live | Additive changes first; else `/v2` + keep v1; track app-version header; deprecation timeline; force-update minimum version |

**Red flag:** no requirement questions; microservices + Kafka + K8s for everything; ignores failures.

---

## 4. Debugging & performance

### Q14. Page takes 4 s to load

**Ask:** A page in our web app takes 4 seconds to load. What do you do?

**Answer — order matters:**

1. Measure: DevTools waterfall — frontend assets, many API calls, or one slow API?
2. Trace the backend (APM/OpenTelemetry).
3. DB: `pg_stat_statements`, `EXPLAIN (ANALYZE, BUFFERS)` — N+1, missing index, `OFFSET` pagination.
4. Fix the cheapest big win: index, `select_related`, smaller payload.
5. Then add caching.
6. Partition very large tables. **Sharding last.**
7. Verify before/after; add an alert.

**Red flag:** first answer is "sharding" or "more servers".

### Q15. p95 200 ms → 3 s after deploy, no errors

**Ask:** After yesterday's deploy, p95 on `/matches` went from 200 ms to 3 s. No errors. Walk me through what you do.

Give information only when they ask.

**Answer:**

1. Scope: all requests or some? p50 too?
2. What changed: diff, migrations, config, flags, dependencies.
3. **Roll back first** if it correlates with the deploy.
4. Investigate: traces, DB locks/CPU, pool saturation, new N+1, dropped index, cache hit rate.
5. Fix, verify, add a regression test/alert, write a blameless postmortem.

**Red flag:** guesses a fix immediately; never mentions rollback.

---

## 5. Legacy, team & delivery

| Ask | Strong answer | Red flag |
| --- | --- | --- |
| How do you handle a messy legacy codebase? | Understand first, characterization tests, fix by pain (incidents, change frequency), strangler fig, feature flags | "Rewrite from scratch" |
| How do you lead 2–3 engineers / a struggling junior? | Clear ownership, delegate with context, reviews that explain *why*, pairing, 1:1s, settle disputes with data | "I fix it myself, faster" |
| Many people, many modules, continuous deploys — how do you keep it safe? | Small PRs, CODEOWNERS, branch protection, CI (lint/types/tests/security), feature flags, staging → canary → prod, one-click rollback, backward-compatible migrations | Long-lived branches; manual deploys from a laptop |

---

## 6. AI & security

### Q16. AI tools in daily work

**Ask:** How do you use AI tools day to day? What do you use them for, what not, and why?

**Answer:**

- **Uses AI for:** boilerplate, tests, drafts, explaining legacy code, learning libraries.
- **Doesn't rely on it for:** security logic, final architecture decisions, production migrations without review.
- Can give an example of AI being wrong.

**Red flag:** "AI writes everything" or refuses AI with no reason.

### Q17. Verifying AI-generated code

**Ask:** How do you check AI-generated code? What makes you confident enough to ship it to production?

**Answer:**

- Review it like a junior's PR — can explain every line.
- Tests + edge cases; `EXPLAIN` the generated SQL.
- Check the docs for any API it used (hallucinations).
- Verify new packages actually exist and are maintained.
- Same CI and review as human code — no shortcut.

**Red flag:** "If it runs, it ships."

### Q18. Security — in AI usage and in the application

**Ask:** How do you handle security, both when using AI tools and in your applications? Which issues do you focus on most, and why?

**Answer:**

- **AI usage:**
  - Never paste secrets, `.env` files, PII or production data
  - Treat user input in LLM prompts as untrusted (prompt injection)
- **Application** — expect them to prioritize, not just list:
  1. Authorization per object (BOLA/IDOR) — #1 API risk
  2. Parameterized queries (no SQL injection)
  3. bcrypt/argon2 for passwords, short-lived tokens + revocation
  4. Secrets in env / Secrets Manager, never in git
  5. Rate limits on login and OTP
  6. Least-privilege IAM; DB in a private subnet
  7. No tokens or PII in logs
  8. Dependency and secret scanning in CI

**Follow-ups:** AWS key pushed to GitHub — what first? (**revoke the key**, then check CloudTrail, then clean history) · Do UUIDs fix IDOR? (no — still need an auth check)

**Red flag:** "We use HTTPS and JWT, so it's secure."

---

## 7. Coding

### Q19. Product of array except self

**Ask:** Given an integer array `nums`, return `answer` where `answer[i]` is the product of all elements except `nums[i]`. Must run in O(n) time and **without division**. Every prefix/suffix product fits in a 32-bit integer.

```text
Input: [1, 2, 3, 4]       → Output: [24, 12, 8, 6]
Input: [-1, 1, 0, -3, 3]  → Output: [0, 0, 9, 0, 0]
```

**Answer:** `answer[i]` = (product of everything left of i) × (product of everything right of i). Two passes, no extra array.

```python
def product_except_self(nums: list[int]) -> list[int]:
    answer = [1] * len(nums)
    prefix = 1
    for i in range(len(nums)):
        answer[i] = prefix
        prefix *= nums[i]
    suffix = 1
    for i in range(len(nums) - 1, -1, -1):
        answer[i] *= suffix
        suffix *= nums[i]
    return answer
```

**Approaches:**

| # | Approach | Time | Extra space | Problem / why |
| --- | --- | --- | --- | --- |
| 1 | Brute force — for each i, multiply all others | O(n²) | O(1) | Too slow for large n (10⁵ → 10¹⁰ ops) |
| 2 | Total product ÷ `nums[i]` | O(n) | O(1) | Not allowed; breaks on zeros (needs 0 / 1 / 2+ zero cases) |
| 3 | Separate `prefix[]` and `suffix[]` arrays | O(n) | O(n) | Correct and clear, but two extra arrays |
| 4 | **Prefix stored in output + running suffix** (code above) | O(n) | O(1)* | **Best** — same idea as #3, no extra arrays |

\*Output array not counted. Good process: #1 → spot repeated work → #3 → optimize to #4 → test with the zero example.

**Follow-ups:** Why is division a bad idea anyway? (breaks on zeros — one zero vs two zeros) · Edge cases? (zeros, negatives, length 2) · Can you do it without the second array? (yes — the code above already does)

**Red flag:** nested loops without noticing O(n²); uses division; doesn't test with an example.

### Q20. Rotate array

**Ask:** Given an integer array `nums`, rotate it to the right by `k` steps (`k` ≥ 0), in place.

```text
Input: [1, 2, 3, 4, 5, 6, 7], k = 3  → Output: [5, 6, 7, 1, 2, 3, 4]
Input: [-1, -100, 3, 99], k = 2      → Output: [3, 99, -1, -100]
```

**Answer:** reverse the whole array, then reverse the first `k`, then reverse the rest. First do `k %= n`.

```python
def rotate(nums: list[int], k: int) -> None:
    n = len(nums)
    k %= n

    def reverse(lo: int, hi: int) -> None:
        while lo < hi:
            nums[lo], nums[hi] = nums[hi], nums[lo]
            lo, hi = lo + 1, hi - 1

    reverse(0, n - 1)
    reverse(0, k - 1)
    reverse(k, n - 1)
```

**Approaches:**

| # | Approach | Time | Extra space | Problem / why |
| --- | --- | --- | --- | --- |
| 1 | Shift by one step, `k` times | O(n·k) | O(1) | Too slow when n and k are large |
| 2 | New array: `new[(i + k) % n] = nums[i]`, copy back | O(n) | O(n) | Correct, but uses a full copy |
| 3 | Slicing: `nums[:] = nums[-k:] + nums[:-k]` | O(n) | O(n) | Most readable in Python; still copies — fine in real code |
| 4 | Cyclic replacements (move each element to its final spot) | O(n) | O(1) | Optimal but tricky — must handle gcd(n, k) cycles; easy to bug |
| 5 | **Reverse all → reverse first k → reverse rest** (code above) | O(n) | O(1) | **Best** — optimal and simple to get right |

Good process: #1 → #2 or #3 → asked for O(1) space → #5. Knowing #4 exists is a bonus.

**Follow-ups:** What if `k` > length? (`k %= n`) · Why `nums[:] = ...` and not `nums = ...`? (slice assignment mutates the caller's list; `=` only rebinds the local name) · Can you do it with O(1) extra space?

**Red flag:** forgets `k % n`; rotates one step at a time without noticing O(n·k); reassigns `nums` and thinks the caller sees it.

---

## 8. DevOps & AWS

### Q21. Deploying to production

**Ask:** How do you deploy a FastAPI/Django service to production with zero downtime?

**Answer:**

- **Build once:** Docker image (multi-stage, slim, non-root), tagged with the **git SHA**, pushed to ECR.
- **Run:** ECS / EKS / EC2 behind an ALB; gunicorn + uvicorn workers; config from env / Secrets Manager.
- **Migrations:** separate step **before** rollout, always backward compatible (expand/contract) — old and new code run together during deploy.
- **Rollout:** rolling, blue-green or canary; **readiness checks** so traffic only reaches healthy instances.
- **Graceful shutdown:** handle `SIGTERM`, finish in-flight requests, ALB connection draining.
- **Rollback:** redeploy the previous image tag — one click.

**Follow-ups:** Migration fails halfway — what now? · Why tag with SHA and not `latest`? (reproducible, knows exactly what runs, easy rollback)

**Red flag:** `git pull` + restart on the server; migrations that break the running version; no rollback plan.

### Q22. CI/CD pipeline

**Ask:** Design a CI/CD pipeline for a backend service in GitHub Actions.

**Answer:**

1. **On PR:** lint, type check, unit + integration tests (real PostgreSQL as a service container), migration check, security scans (secrets, dependencies, SAST).
2. **On merge to main:** build image → tag with SHA → push to ECR.
3. **Deploy to staging** → smoke tests.
4. **Deploy to production:** automatic or manual approval; canary → full rollout; watch metrics; auto-rollback on errors.

- AWS access via **OIDC** role — no long-lived AWS keys stored in GitHub.
- Cache dependencies for speed; keep pipeline under ~10 min.
- Feature flags to separate deploy from release.

**Follow-ups:** How do you keep the pipeline fast? · Tests are flaky — what do you do? (fix or quarantine; never "just re-run")

**Red flag:** deploys from a laptop; no tests in CI; AWS root/admin keys in secrets.

### Q23. Scaling a service

**Ask:** Traffic grows 10×. How do you scale the app, the workers and the database?

**Answer:**

- **App:** stateless (sessions in Redis/JWT, files in S3) → **horizontal scaling** behind a load balancer; auto scaling on CPU / RPS / latency.
- **Workers:** scale on **queue length**, not CPU.
- **Database** (usually the real bottleneck):
  - Connection pooling — PgBouncer / RDS Proxy
  - Fix slow queries and indexes first
  - Cache hot reads
  - **Read replicas** for reads (watch replica lag)
  - Vertical scaling; partitioning; sharding last
- **Edge:** CDN for static and cacheable responses.
- **Load test** before big events (k6 / Locust); pre-scale for predictable spikes.

**Follow-ups:** 20 app instances × 20 connections each — what happens to PostgreSQL? (exceeds `max_connections` → use a pooler) · User writes data, reads from replica, doesn't see it? (replica lag → read-your-writes from primary)

**Red flag:** "add more servers" while the DB is the bottleneck; stateful app servers.

### Q24. AWS networking & IAM

**Ask:** How do you set up VPC, security and access for a production app on AWS?

**Answer:**

- **VPC across 2+ AZs:**
  - Public subnets → ALB, NAT gateway
  - Private subnets → app servers
  - Isolated subnets → RDS, ElastiCache
- **Security groups:** DB accepts traffic only from the app's security group; no `0.0.0.0/0` on the DB or SSH (use SSM Session Manager).
- **IAM:** roles for EC2/ECS tasks — **no access keys on servers**; least privilege per service; MFA, no root usage.
- **S3:** block public access; share files with **pre-signed URLs**.
- **DNS & TLS:** Route 53 + ACM certificates on the ALB.
- **Cost:** VPC endpoints for S3 (avoid NAT data charges), right-sizing, budgets/alerts.

**Follow-ups:** Security group vs NACL? (SG stateful, per instance; NACL stateless, per subnet) · How does an app in a private subnet call an external API? (NAT gateway)

**Red flag:** DB in a public subnet; AWS keys hardcoded on EC2; everyone has admin access.

### Q25. Monitoring, alerting & infrastructure as code

**Ask:** How do you know production is healthy, and how do you manage infrastructure changes?

**Answer:**

- **Metrics:** RED for services (rate, errors, duration p95/p99); USE for resources (CPU, memory, connections) — Prometheus/CloudWatch + Grafana.
- **Logs:** structured JSON with request ID (Loki / CloudWatch Logs); no PII or tokens.
- **Traces:** OpenTelemetry across API → DB → queue → external calls.
- **Alerts on user-facing symptoms** (error rate, latency SLO, queue backlog) — not every CPU spike; each alert has a runbook.
- **IaC:** Terraform (or CloudFormation/CDK); remote state with locking; `plan` reviewed in a PR before `apply`; no console click-ops in production.

**Follow-ups:** What would you alert on for this service? · Someone changed infra in the console — what's the problem? (drift; next `apply` may revert or break it)

**Red flag:** finds out about outages from users; alert fatigue; infra only in someone's head.

---

## Scorecard

| Dimension | Qs | 1–4 | Notes |
| --- | --- | --- | --- |
| Python & concurrency | Q1 | | |
| PostgreSQL, transactions & ORM | Q2–Q4, Q6–Q7 | | |
| API design & async workflows | Q8–Q11 | | |
| Caching | Q5 | | |
| Own system / ownership | §2 | | |
| Tech choices & system design | Q12–Q13 | | |
| Structured debugging | Q14–Q15 | | |
| Legacy, team & delivery | §5 | | |
| AI judgement | Q16–Q17 | | |
| Security | Q18 | | |
| Coding | Q19–Q20 | | |
| DevOps & AWS | Q21–Q25 | | |

**1** no hire · **2** knows terms, shallow · **3** hire — reasons through trade-offs · **4** strong — raises issues before asked

**Hire bar:** no 1s; at least 3 in PostgreSQL, System design, Debugging, Security. Gaps in Kafka, Elasticsearch, Terraform or LLM work are fine — the 3-month training covers them.

---

## Question list (quick sheet for the interview)

Questions only. Answers are in the sections above.


### Coding

1. Given an integer array `nums`, return `answer` where `answer[i]` is the product of all elements except `nums[i]` — in O(n), without division.
    - Example: `[1, 2, 3, 4]` → `[24, 12, 8, 6]`
    - Example: `[-1, 1, 0, -3, 3]` → `[0, 0, 9, 0, 0]`
    - Why is division a bad idea? What edge cases do you test?
2. Given an integer array `nums`, rotate it to the right by `k` steps (`k` ≥ 0), in place.
    - Example: `[1, 2, 3, 4, 5, 6, 7]`, k = 3 → `[5, 6, 7, 1, 2, 3, 4]`
    - Example: `[-1, -100, 3, 99]`, k = 2 → `[3, 99, -1, -100]`
    - What if `k` is larger than the array length? Can you do it with O(1) extra space?



### 1. Fundamentals

3. What is the GIL? Concurrency vs parallelism? When do you use threads, asyncio, processes?
   - FastAPI `def` vs `async def` — what's the difference?
   - What happens if you call `time.sleep()` inside an `async def` endpoint?
4. What is a transaction and why does it matter? What are isolation levels?
   - Give an example of write skew.
   - You save an order, then send a Celery task — what can go wrong?
5. When should logic live in a PL/pgSQL function or trigger? When is that a mistake?
   - How do you write safe dynamic SQL in PL/pgSQL?
   - What is the risk of `SECURITY DEFINER`?
6. How do you add a NOT NULL column to a 50M-row production table without downtime?
   - How do you create an index without blocking writes?
   - How do you rename a column safely?
7. When do you cache? Which pattern? How do you invalidate? LRU or LFU?
   - A hot key expires and 5k requests hit the DB — what is that, how do you prevent it?
   - Redis goes down — what happens to the DB?
8. Two requests update the same row at the same moment — what happens and how do you keep it correct?
   - What is a deadlock and how do you avoid it?
   - How do many workers take jobs from a PG table without taking the same one?
9. When do you use an ORM and when do you write raw SQL?
   - How do you spot N+1 queries in production?
   - Raw SQL with user input — how do you keep it safe?
10. How do you design a production-grade REST API?
   - 401 vs 403? PUT vs PATCH?
   - Why cursor pagination over offset?
11. When do you use REST, GraphQL, gRPC, WebSocket or SSE?
   - Why not GraphQL for everything?
12. What is event-driven architecture? Pros, cons, when to use it?
    - The DB commit succeeded but the event wasn't published — how do you prevent that?
    - A consumer receives the same event twice — what happens?
13. How do you handle async / background tasks?
    - The worker crashes in the middle of a task — what happens?
    - Why pass an ID to a task instead of the whole object?


### 2. Tech choices & system design

14. For a new service, how do you choose the language, framework and database? PostgreSQL or MongoDB?
    - When is MongoDB the wrong choice?
    - When would you **not** add a new technology even though it fits?
15. Design one: **live match scores** / **notification service** / **face verification service**.
    - Now 10× the traffic on match day.
    - Mobile users are on slow 3G, and some go offline.
    - Redis just died.
    - The mobile team needs a breaking API change, but old app versions are still in use.

### 3. Debugging & performance

16. A page in our web app takes 4 seconds to load. What do you do?
17. After yesterday's deploy, p95 on `/matches` went from 200 ms to 3 s. No errors. Walk me through it.

### 4. Legacy, team & delivery

18. How do you handle a messy legacy codebase that's in production?
19. How do you lead 2–3 engineers? How do you help a struggling junior?
20. One repository, Many engineers, many modules, continuous deploys — how do you keep it safe?

### 5. AI & security

21. How do you use AI tools day to day? What for, what not, and why?
22. How do you check AI-generated code before shipping it to production?
23. How do you handle security in AI usage and in your applications? Which issues matter most, and why?
    - An AWS key was pushed to GitHub — what do you do first?
    - Do UUIDs fix IDOR?





### 6. Current Working project

24. Draw your system. Walk one request client → DB → response. Where is each piece of state stored?
25. Roughly what are your RPS, DB size and p95 latency?
26. What breaks if Redis / the DB / the queue / a third-party API goes down?
27. Tell me about a decision **you** made. What alternative did you reject, and why?
28. If you rebuilt it today, what would you change?

### 7. DevOps & AWS

29. How do you deploy a FastAPI/Django service to production with zero downtime?
    - A migration fails halfway through the deploy — what now?
    - Why tag images with the git SHA and not `latest`?
30. How do you Design a CI/CD pipeline for a backend service.
    - How do you keep the pipeline fast? What do you do with flaky tests?
31. Traffic grows 10×. How do you scale the app, the workers and the database?
    - 20 app instances × 20 DB connections each — what happens to PostgreSQL?
    - A user writes data, then reads from a replica and doesn't see it — why?
32. How do you set up VPC, security and access for a production app on AWS?
    - Security group vs NACL?
    - How does an app in a private subnet call an external API?
33. How do you know production is healthy, and how do you manage infrastructure changes?
    - What would you alert on for this service?
    - Someone changed infra in the AWS console — what's the problem?














Senior Backend Engineer:

Senior Backend Engineer @ Spordium
In Office @Banani, Dhaka, Bangladesh.


About the Job:

First, We're looking for a Senior Backend Engineer to own systems end to end — from database design and API contracts through deployment and monitoring. Based on where you are and where we like you to be we will identify knowledge gaps and train you in those areas both theoretically and practically. Based on your improvement and abilities you will be assigned small tasks to prove that you are ready to come on board in the mainstream product line.
Whichever professional (intermediate, advanced) stage you join, you will go through the above process for the first three months. It will totally depend on your abilities and how fast you reach the last line to cross over to the mainstream team.
Successfully completing the above-mentioned screening process, you will be assigned responsibilities accordingly. When assigned a responsibility you will work from Spordium’s office in Banani, your job location will be on-premise. Spordium will provide you with all the necessary equipment needed for your specific task.

Responsibilities:
•	Build new backend services and APIs from scratch, and ship them to production
•	Work in an existing legacy codebase: fix bugs, pay down technical debt, get it production-ready
•	Lead a team of 2–3 engineers, and mentor junior and mid-level engineers through code review and pairing
•	Own features end to end, including what happens after release
•	Design PostgreSQL schemas that hold up as the product grows — indexing, transactions, safe migrations
•	Write and optimize complex queries and PL/pgSQL functions, and profile slow APIs
•	Collaborate closely with the web and mobile teams, shaping API contracts around how clients actually consume them
•	Design for scale — service boundaries, capacity planning, a codebase that stays manageable
•	Build asynchronous workflows: background jobs, queues, retries, idempotency
•	Work on real-time communication systems and scale WebSocket services
•	Instrument services with metrics, logs, and dashboards so failures surface early

Remuneration Details:

*We are always looking for Promising Engineers. 
Minimum full-time salary ranges between BDT 75,000 to BDT 95,000.
*One festival bonus per year on Full Gross salary.
*Tax on salary, if applicable, will be deducted at source.
*PF & Gratuity are available to be availed by the employee.

Minimum Qualification:

Bachelor's degree in Computer Science, Software Engineering, or a closely related field from a recognized university
*Equivalent practical experience with a strong portfolio of shipped production apps will also be considered

Preferred Qualification:

•	3-5 years building and running production backend systems
•	Experience leading a small team (2–3 engineers) — delegating, reviewing, and mentoring
•	Strong Python (FastAPI, Django, or similar), or equally strong in another backend language with willingness to work in Python
•	Solid OOP fundamentals and working knowledge of SOLID, DRY, KISS, and YAGNI — including the judgement to know when a principle applies and when applying it would add complexity for no return
•	Deep PostgreSQL knowledge: schema design, normalization tradeoffs, indexing strategy, transactions and isolation levels, query planning and tuning
•	Comfortable writing PL/pgSQL functions, triggers, and views where they're the right tool
•	Solid grasp of API design best practices — resource modeling, pagination, error handling, authentication/authorization, backward-compatible versioning
•	Practical experience with Redis, Kafka, RabbitMQ, or similar for caching, queues, or streams
•	Working understanding of how web and mobile clients consume APIs, and the judgement to make backend decisions that account for their constraints (offline behavior, payload size, latency, versioning)
•	Experience designing and running a microservices architecture — service boundaries, inter-service communication, failure isolation
•	Understanding of scaling strategies: horizontal scaling, load balancing, caching layers, read replicas, connection pooling
•	Linux server administration and hands-on AWS experience (EC2, IAM, VPC, S3, Route 53 or equivalents)
•	Git-based workflow and code review discipline

Candidates with knowledge and hands-on experience in the following areas will be given priority:

•	Experience with MongoDB or another document store, and knowing when it's the right choice over a relational model
•	Elasticsearch — index design, analyzers, relevance tuning, and keeping indexes in sync with the primary database
•	CI/CD tooling — Jenkins, GitHub Actions, AWS CodeDeploy
•	Observability stacks — Prometheus, Loki, Grafana, or OpenTelemetry
•	Infrastructure as code (Terraform, Ansible)
•	Experience introducing engineering practices — testing standards, code review culture, documentation — to a growing team
•	Integrating LLM APIs into production services
•	Vector search and embeddings — pgvector, Qdrant, or similar
•	Designing backend workflows around AI calls
•	Serving ML or computer-vision model inference behind an API


Apply via Linkedin Job Post or send your CV career@spordium.com mentioning "Senior Backend Engineer" in the subject line.

Office Address:
Spordium
Flat A4, House 25, Road 4, Block F, Banani, Dhaka - 1213, Ba