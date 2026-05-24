# Understanding Rate Limiting

## What is rate limiting?

Rate limiting is a technique used to control how many requests a client can send to an API or server within a given time period. When the limit is crossed, extra requests are either blocked, delayed, or rejected.

**Example:** An API allows only 100 requests per minute per user. If a user crosses this limit, further requests are temporarily blocked. The same API may also allow only 1,000 requests per minute from all users combined, so when heavy traffic comes in, rate limiting protects the system from overload.

---

## Why is rate limiting necessary?

Rate limiting protects your system from many problems — both malicious and accidental. It blocks DDoS attacks, brute force attacks, credential stuffing, inventory hoarding, and data scraping by capping how many requests a client can send.

It also helps you keep resources available for real users and prevents one heavy user from slowing the system down for everyone.

**Main reasons to use rate limiting:**

1. **Prevent abuse and improve security** — Stop bots, scrapers, and attackers from overwhelming your system.
2. **Improve performance** — Keep response times stable under heavy load.
3. **Control cost** — Cloud bills (compute, bandwidth, database) grow with traffic. Limits keep cost predictable.
4. **Ensure fair usage** — No single user can consume all the resources.
5. **Enforce pricing tiers** — Free users get 100 requests/hour, Pro users get 10,000, Enterprise gets unlimited. Rate limiting is how you actually enforce these tiers.
6. **Stay within third-party limits** — When you call external APIs (Stripe, GitHub, OpenAI), they enforce their own limits. You rate-limit yourself outbound so you don't get banned.

---

## Common use cases

Rate limiting is used in many places to control traffic, prevent abuse, and keep resource usage fair and stable:

- **API rate limiting** — Cap requests per API key or per user on public APIs.
- **Web server rate limiting** — Protect a server from sudden traffic spikes.
- **Database rate limiting** — Limit how many queries or connections hit the database.
- **Login rate limiting** — Block brute force attacks on login or password reset endpoints.

### Real-world examples

- **Google Maps API** — A popular API and a frequent target of malicious traffic. Google uses rate limiting to keep the service available for legitimate users.
- **GitHub API** — Used by millions of developers. GitHub limits API calls so heavy users don't slow down the platform for others.
- **Twitter API** — Used to post tweets, fetch user data, and more. Twitter rate-limits to block spammy and abusive usage.
- **Cloudflare** — A CDN and security service. It rate-limits traffic at the edge to block DDoS attacks before they reach origin servers.

---

## Types of rate limiting

Rate limiting can be applied based on *who* or *what* is making the request. Here are the most common types.

### 1. IP-based rate limiting

Limits the number of requests from a single IP address within a time period. Often used to block bots and basic denial-of-service attacks.

**Example:** An online retailer allows only 10 requests per minute per IP. Bots trying to scrape product data get blocked, but normal users can browse without any issue.

**Pros:**

- Simple to set up at both the network and application level.
- Effective against basic abuse from a single source.

**Cons:**

- Can be bypassed using VPNs, proxies, or botnets.
- May block legitimate users sharing the same IP (for example, users behind a corporate NAT or a university network).

### 2. Server-based rate limiting

Limits the number of requests a single server will handle within a time period. The goal is to keep each server within its safe capacity.

**Example:** A music streaming service allows only 100 requests per second per server. This keeps the system fast and responsive even during peak hours.

**Pros:**

- Protects each server from getting overwhelmed.
- Keeps performance stable across all users.

**Cons:**

- In a distributed system, attackers can spread requests across many servers and bypass the per-server limit.
- Real users may face delays if the limit is too strict or traffic is unusually high.

### 3. Geography-based rate limiting

Limits requests based on the geographic location of the user's IP. Useful when traffic from certain regions is risky, or when you must follow regional rules.

**Example:** A social media platform sees heavy bot activity from one region, so it limits requests from that region to 10 per minute to reduce spam and fake accounts.

**Pros:**

- Reduces malicious traffic from high-risk regions.
- Helps comply with regional laws (data residency, sanctions, etc.).

**Cons:**

- VPNs and proxies can easily bypass it.
- Real users traveling abroad or using international networks may get blocked.

### 4. User-based rate limiting

Limits requests based on the user account, not the IP. This is the most accurate type because it follows the user across devices, networks, and sessions.

**Example:** A SaaS app allows each free user to make 100 API calls per hour and each Pro user to make 10,000. The limit is tied to the user ID, not the IP.

**Pros:**

- Hard to bypass — switching VPN or device doesn't reset the limit.
- Works well for enforcing pricing tiers and per-user fairness.

**Cons:**

- Needs authentication, so it doesn't work for anonymous traffic.
- Requires reliable user identification across sessions, which adds complexity.

---

## Rate limiting algorithms

These are the algorithms that actually decide whether a request is allowed or blocked.

### 1. Token bucket algorithm

**How it works:** Imagine a bucket that holds tokens. New tokens are added at a fixed rate (for example, 1 token every 10 seconds). Every incoming request must take 1 token to pass. If the bucket is empty, the request is blocked. Unused tokens stay in the bucket up to its maximum size, so the user can save them and use them later as a small burst.

**Easy example:**

- Bucket size: 5 tokens. Refill rate: 1 token per minute.
- You don't send any requests for 5 minutes → bucket fills up to 5 tokens.
- Suddenly you send 5 requests in 1 second → all 5 are allowed (this is the burst).
- The 6th request right after → blocked, because the bucket is empty.
- Wait 1 minute → 1 new token is added → 1 more request is allowed.

**Pros:**

- Allows short bursts, which feels natural for real users.
- Smooth and easy to tune (set bucket size and refill rate).

**Cons:**

- Slightly more complex to implement than fixed windows.
- A big burst can still hit your backend hard if the bucket is too large.

### 2. Leaky bucket algorithm

**How it works:** Think of a bucket with a small hole at the bottom. Requests pour in from the top and leak out from the bottom at a fixed steady rate. If too many requests come in too fast and the bucket overflows, the extra ones are dropped. The output rate is always smooth, no matter how the input looks.

**Easy example:**

- Bucket size: 5 requests. Leak rate: 1 request per second.
- 5 requests arrive at the same time → all 5 are queued in the bucket.
- They are processed 1 per second.
- While they are being processed, 10 more requests arrive → since the bucket is full, those 10 are dropped.

**Pros:**

- Output traffic is always smooth and predictable.
- Great for protecting a downstream system that can only handle a steady rate.

**Cons:**

- Bursts are not allowed at all, even when the system has spare capacity.
- Real users may feel the system is slow during sudden spikes.

### 3. Fixed window counter

**How it works:** Time is divided into fixed windows (for example, every 1 minute). For each window, you keep a counter. Every request increases the counter by 1. If the counter reaches the limit, all further requests in that window are blocked. When the next window starts, the counter resets to 0.

**Easy example:**

- Limit: 5 requests per minute.
- Between 10:00:00 and 10:00:50 → user sends 5 requests → all allowed.
- At 10:00:55 → user sends 2 more requests → blocked (counter is already 5).
- At 10:01:00 → new window starts, counter resets → requests allowed again.

**Pros:**

- Very simple and cheap to implement (just one counter per user).
- Easy to reason about for users and developers.

**Cons:**

- The boundary problem: a user can send 5 requests at 10:00:59 and 5 more at 10:01:00 — 10 requests in 1 second, even though the limit is "5 per minute."
- Traffic can look bursty right at window boundaries.

### 4. Sliding window log

**How it works:** Instead of a counter, you store a timestamp for every request the user makes. When a new request comes in, you look at the log and count how many requests happened in the last N seconds. If the count is over the limit, you block the request. Old timestamps (outside the window) are removed.

**Easy example:**

- Limit: 5 requests per minute.
- User sends 5 requests between 10:00:00 and 10:00:40 → all allowed, all 5 timestamps saved.
- At 10:00:50 → user sends another request → log shows 5 requests in the last 60 seconds → blocked.
- At 10:01:10 → timestamps before 10:00:10 expire and are removed → log now shows 4 → new request is allowed.

**Pros:**

- Very accurate. No boundary problem like the fixed window.
- Limit is enforced based on a true rolling window.

**Cons:**

- Memory cost grows with the number of requests, since you store a timestamp for every request.
- Slower at very high scale because you need to clean up old entries on every check.

### 5. Sliding window counter

**How it works:** A mix of fixed window and sliding window log. You keep counters for the current window and the previous window. When a request comes in, you take the full count from the current window plus a fraction of the previous window's count, based on how far into the current window you are. This gives you the smoothness of a sliding log with the cheap memory of a fixed window.

**Easy example:**

- Limit: 100 requests per minute.
- Previous window (10:00 – 10:01) had 80 requests. Current window (10:01 – 10:02) has 30 requests so far.
- A new request arrives at 10:01:30 — that's 50% into the current window.
- Estimated count = 30 (current) + 80 × 50% (previous) = 30 + 40 = 70.
- 70 < 100 → request is allowed.

**Pros:**

- Almost as accurate as sliding window log, but much cheaper.
- Smooths out the boundary problem of the fixed window.

**Cons:**

- It's an approximation, not exact — the math assumes traffic in the previous window was spread evenly, which isn't always true.
- Slightly more complex to implement than a plain fixed window.

---

## Where to apply rate limiting (the layers)

Real production systems don't pick just one layer. They apply rate limiting at multiple layers because each layer catches different problems.

### Layer 1: Edge / CDN (Cloudflare, AWS WAF, Fastly)

The outermost ring. Cloudflare, AWS WAF, or your CDN enforces limits based on IP, ASN, country, or fingerprint before traffic even reaches your infrastructure.

- **Use case:** Block volumetric DDoS attacks, scrapers, and obvious bot traffic. Rules look like "max 1000 req/min per IP" or "challenge IPs from suspicious ASNs."
- **Why here:** Traffic blocked here costs you nothing — you don't pay for bandwidth or compute on requests that never reach your origin.

### Layer 2: Load balancer / API gateway (Nginx, ALB, Kong, AWS API Gateway)

This is where most "first-class" rate limiting happens in production. Nginx's `limit_req_zone`, Kong's rate-limiting plugin, AWS API Gateway usage plans, Envoy's rate limit service — all sit here.

- **Use case:** Per-API-key, per-user, per-route limits. "This endpoint allows 100 req/min per API key." "Login endpoint allows 5 req/min per IP."
- **Why here:** It's centralized, fast (in-memory or Redis-backed), and protects every downstream service uniformly. Your application code stays clean.

### Layer 3: Application layer (FastAPI, Django middleware)

In-app rate limiting using libraries like `slowapi` (FastAPI), `django-ratelimit`, or custom middleware backed by Redis.

- **Use case:** Business-logic limits that need application context. "User can create 10 projects per day." "Free tier can run 5 expensive ML inferences per hour." "Same user can't request password reset more than 3 times per hour."
- **Why here:** The gateway doesn't know your domain model. It doesn't know what a "project" is or which user is on the free tier. Application code does.

### Layer 4: Service-to-service (internal mesh)

In a microservice architecture, services rate-limit each other. Service A calls Service B — Service B applies limits per calling service. Istio, Linkerd, or Envoy sidecars handle this.

- **Use case:** Protect an internal service from a misbehaving sibling. If your notification service starts looping and floods the user service, internal rate limiting saves you.

### Layer 5: Database / resource layer

Connection pools (PgBouncer), query timeouts, and statement-level limits are also a form of rate limiting. PostgreSQL's `statement_timeout`, connection pool `max_connections`, Redis `maxmemory-policy` — all of these bound how much load reaches the storage tier.

### Layer 6: Outbound / client-side

When *you* are calling someone else's API, you rate-limit yourself. Token bucket libraries wrap your HTTP client so you don't exceed Stripe's, OpenAI's, or GitHub's published limits and get banned.

---

## The common production pattern

In a typical setup (FastAPI/Django + PostgreSQL + Redis on AWS), you'd usually see:

- **CloudFront / AWS WAF** at the edge for IP-based volumetric protection.
- **ALB or Nginx** for coarse per-IP limits at the load balancer.
- **API Gateway or Nginx** for per-API-key route-level limits (e.g., "100 req/min per key on `/search`").
- **FastAPI/Django middleware** backed by Redis for per-user business limits, using token bucket or sliding window algorithms.
- **Internal service limits** if you have multiple backends talking to each other.
- **PgBouncer** in front of PostgreSQL to bound connection-level pressure.

---

## Implementation challenges

Rate limiting sounds simple, but it gets tricky in production. The most common challenges are:

- **Latency** — Every request has to check a counter (often in Redis). If the check is slow or Redis is far away, every request gets slower. Keep the check fast and close to the app.
- **False positives** — Legitimate users behind a shared IP (corporate networks, mobile carriers) can get blocked by IP-based limits. Mix IP and user-based limits to reduce this.
- **Distributed counting** — In a multi-pod or multi-region setup, the counter must be shared. A local in-memory counter on each pod won't enforce a global limit. Most teams use Redis or a similar shared store.
- **Configuration complexity** — Picking the right limit is hard. Too strict blocks real users, too loose lets abuse through. Start with sensible defaults, log everything, and tune based on real traffic.
- **Scalability** — At very high traffic, even Redis can become a bottleneck. Solutions include sharding the counter, using local approximations, or moving simple limits to the edge.

---

## Client-side vs server-side rate limiting

- **Server-side** is the real protection. You can't trust the client, so the server must enforce limits. This is what blocks attackers and abusers.
- **Client-side** is a courtesy and a cost control. A well-behaved client (your mobile app, your background worker calling Stripe) throttles itself so it doesn't waste requests, doesn't get banned by upstream APIs, and gives a smoother user experience.

In short: always enforce on the server, and add client-side throttling whenever you are the one *calling* an external API.
