---
title: "Rate Limiting Algorithms: How They Work and When to Use Each"
date: 2026-06-06
type: article
tags: [rate-limiting, system-design, backend, api]
---

## Intro

As a backend engineer, I have hit rate limits from both sides — protecting my own APIs from abuse, and getting blocked by third-party APIs I was calling. Over time I learned that "rate limiting" is not one thing; it is a family of algorithms, and picking the wrong one quietly hurts either your users or your servers. This article breaks down the five algorithms I keep coming back to: how each one works, its trade-offs, and where it fits.

## Rate Limiting: What and Where

A rate limiter controls how many requests a client can make within a time window — for example, capping a user at **100 requests per minute**. Its main job is to **protect backend infrastructure** from abuse, overload, and DoS, while also controlling cost, ensuring fair usage, and enforcing pricing tiers. It can run at many layers — client, CDN/edge (Cloudflare), web server, API gateway, microservice, or database — and you identify clients by IP, user, API key, or region. Most of the time you should reuse what the edge or gateway already provides; you build your own only when you need application logic they don't have. The classic case is **user-based limiting for pricing tiers** — e.g. free ChatGPT/Claude vs. Pro: same endpoint, different quotas based on who you are.

Now let's look at the five core algorithms.

---

## 1. Leaky Bucket

Picture a bucket with a small hole at the bottom. Requests pour in from the top and leak out from the bottom at a **fixed, steady rate**. If requests come in too fast and the bucket overflows, the extra ones are dropped. The output is always smooth, no matter how messy the input is.

**Example**

- Bucket size: 5 requests. Leak rate: 1 request per second.
- 5 requests arrive at once → all 5 are queued in the bucket.
- They are processed 1 per second.
- While they are still processing, 10 more arrive → the bucket is full → those 10 are dropped.

**Pros —** Output is smooth and predictable; great for protecting a downstream system that can only handle a steady rate.

**Cons —** No bursts allowed even when capacity is free, so real users may feel it's slow during spikes.

**When to use —** Protecting fragile downstream services, or shaping outbound traffic (async workers, proxy/gateway) where a small delay is fine. *Real-world: bandwidth management, video streaming.*

---

## 2. Token Bucket

A bucket holds **tokens**. New tokens are added at a fixed rate (say, 1 every 10 seconds). Every request must take 1 token to pass. If the bucket is empty, the request is blocked. Unused tokens stay in the bucket up to its max size — so a quiet user can save tokens and spend them later as a **short burst**.

**Example**

- Bucket size: 5 tokens. Refill rate: 1 token per minute.
- You send nothing for 5 minutes → bucket fills to 5 tokens.
- You suddenly send 5 requests in 1 second → all 5 pass (the burst).
- The 6th request right after → blocked, bucket is empty.
- Wait 1 minute → 1 new token → 1 more request allowed.

**Pros —** Allows short bursts that feel natural for real users; easy to tune with just bucket size and refill rate.

**Cons —** A bit more complex than fixed windows, and too large a bucket lets a big burst still hit your backend hard.

**When to use —** User-facing APIs where short bursts are fine (e.g. a mobile app batching on launch), payment/messaging APIs with a steady average, or per-user/per-API-key throttling. *Real-world: Stripe, AWS API throttling.*

> **Leaky vs. Token, the key difference:** leaky bucket smooths output and *forbids* bursts; token bucket *allows* saved-up bursts. Both use a "bucket," but one drains at a fixed rate, the other fills at a fixed rate.

---

## 3. Fixed Window Counter

Time is split into fixed windows (e.g. every 1 minute). Each window has a counter. Every request adds 1. When the counter hits the limit, all further requests in that window are blocked. When the next window starts, the counter resets to 0.

**Example**

- Limit: 5 requests per minute.
- 10:00:00–10:00:50 → user sends 5 requests → all allowed.
- 10:00:55 → user sends 2 more → blocked (counter is already 5).
- 10:01:00 → new window starts, counter resets → allowed again.

**Pros —** Very simple and cheap (one counter per user), and easy for both users and developers to reason about.

**Cons —** The *boundary problem*: a user can send 5 requests at 10:00:59 and 5 more at 10:01:00 — 10 in ~1 second despite a "5 per minute" limit — so traffic spikes at window edges.

**When to use —** Simple API limits (e.g. 100/minute), login throttling, or anywhere simplicity and low memory matter more than exact boundaries. *Real-world: basic API rate limiting, access control.*

---

## 4. Sliding Window Log

Instead of a counter, you store a **timestamp for every request**. When a new request comes in, you count how many timestamps fall in the last N seconds. If that count is over the limit, you block it. Old timestamps outside the window are removed.

**Example**

- Limit: 5 requests per minute.
- 10:00:00–10:00:40 → user sends 5 requests → all allowed, 5 timestamps saved.
- 10:00:50 → another request → log shows 5 in the last 60s → blocked.
- 10:01:10 → timestamps before 10:00:10 expire → log shows 4 → new request allowed.

**Pros —** Very accurate with no boundary problem; enforces a true rolling window.

**Cons —** Memory grows with request count (one timestamp each), and it's slower at high scale since old entries are cleaned on every check.

**When to use —** High-value APIs where accuracy matters (payments, authentication), cases needing exact timestamps for auditing, or low-to-medium request volume per client.

---

## 5. Sliding Window Counter

A mix of fixed window and sliding window log. You keep counters for the **current** and **previous** windows. For each request, you take the full current count plus a **fraction of the previous count**, based on how far you are into the current window. You get most of the accuracy of the log with the cheap memory of a counter.

**Example**

```
Previous window (12:00–12:01): 8 requests
Current window  (12:01–12:02): 6 requests, 42 seconds in (70% through)

Estimated count = current + (1 - 0.70) × previous
                = 6 + 0.30 × 8
                = 6 + 2.4
                = 8.4

Limit = 10 → 8.4 < 10 → ALLOW ✅
```

**Pros —** Almost as accurate as the sliding window log but much cheaper, and it smooths out the fixed window's boundary problem.

**Cons —** It's an approximation (the math assumes the previous window's traffic was spread evenly), and a bit more complex than a plain fixed window.

**When to use —** The best middle ground for most apps — API gateways and middleware that want good accuracy without per-request storage, and high-volume limiting where memory matters.

---



## Redis Rate Limiting Best Practices
A few things I've learned using Redis for rate limiting in production
INCR plus EXPIRE looks simple, but a few rough edges only show up under real traffic. First: never run them as two separate calls. If something crashes between them, you get a counter key that never expires, and across thousands of API keys that's a slow memory leak. Wrapping both inside MULTI/EXEC, or better, a small Lua script with EVAL, fixes this since Redis treats it as one atomic step. I moved to Lua scripts early on, mainly because it's also one round trip instead of two.
Second: keep key names predictable, like ratelimit:[api-key]:[minute]. It sounds minor, but it makes debugging in redis-cli much faster when you're chasing down why a specific user got blocked.
Third, and this one actually bit me: a plain per-minute counter has a boundary problem. A user can fire 20 requests in the last second of one window and 20 more in the first second of the next, getting 40 through in two seconds even though both windows passed the check individually. For most APIs this doesn't matter, but for anything expensive, like payments or search, it can hurt. The fix is a sliding window using a Redis sorted set instead of a flat counter.
Last note: I've used both hand-rolled Redis limiters and built-in ones from gateways like Kong and AWS API Gateway. The built-in ones are fine for simple "X per minute" rules, but once you need custom logic, like per-tier limits, you end up writing your own anyway. Redis stays my go-to since INCR and EXPIRE map directly to the problem and the code is easy for anyone to follow.

## Challenges Of Rate limiter

1. The Race Condition Problem

2. Distributed State Consistency: A single server rate limiting is trivial. The moment you have multiple gateway instances, they must share state — otherwise each thinks it's the only one counting.

3.  Clock Skew Across Servers: Token bucket and sliding window algorithms both depend on timestamps. If Gateway A's clock is 200ms ahead of Gateway B's clock, they'll calculate different refill amounts for the same user. At scale, this causes:

Over-counting refills (users get more requests than allowed)
Under-counting (users get throttled unfairly)

4. The Thundering Herd at Window Boundaries

5. Choosing the Right Granularity

6. Cold Start / New User Problem

7. Identifying the Right Client: This sounds simple — use the user ID. But in practice:

Unauthenticated users: you fall back to IP address — but NAT means thousands of users can share one IP (office networks, mobile carriers). Block the IP and you've blocked everyone behind that NAT.
Authenticated users behind proxies: X-Forwarded-For header can be spoofed. A malicious client can rotate headers to appear as different IPs.
API keys: if a key is shared or leaked, the legitimate owner gets throttled because an attacker is burning their quota.

There's no perfect identifier — you pick the least-bad option per context and accept the trade-offs.


8. What To Do When Redis Goes Down

9. Algorithm Parameter Tuning

10. Monitoring and Observability Blind Spots


## Conclusion

There is no single "best" rate limiter — there's the one that fits your traffic shape and constraints. If you want a safe default, **sliding window counter** gives you accuracy and low memory. If your users naturally burst, reach for **token bucket**. If you must protect a fragile downstream at all costs, **leaky bucket**. And if you're just starting and want something dead simple, **fixed window counter** is fine — just know about its boundary problem before it surprises you in production.
