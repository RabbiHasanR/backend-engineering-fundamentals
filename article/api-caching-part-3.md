# The Complete Guide to Application Layer Caching Part 3: Expiration, Eviction, and Production Tuning

So far we've covered the **foundations** of application layer caching ([Part 1](#)) and the **design patterns** that decide how the cache and database work together ([Part 2](#)). But no matter which pattern you pick, two things ultimately decide whether your cache helps or hurts in production: **when data expires**, and **what gets thrown out when the cache fills up**.

Getting these two right is the difference between a cache that saves your database and one that quietly serves stale data to your users.

---

## Time-To-Live (TTL)

TTL tells the cache how long a piece of data should live before it's automatically removed or refreshed. Setting a good TTL reduces the risk of serving outdated information without needing you to manually invalidate anything. For example, setting a 10-minute TTL on product inventory ensures stock levels refresh regularly, keeping them reasonably accurate without manual intervention.

The right TTL depends on four things: how often the data changes, how much staleness your users can tolerate, how expensive a cache miss is, and how much freshness actually matters. Dynamic data like real-time pricing needs very short TTLs (seconds), while static data like country codes or currency lists can safely live in the cache for hours or days.

In layered systems where caches exist at the browser, CDN, API gateway, and database level, it's common to use a **TTL hierarchy**: shorter TTLs at the edges (browser, CDN) and longer ones deeper in the stack (application, database cache). This balances freshness with efficiency.

---

## Eviction: What Happens When the Cache Fills Up

TTLs control when data expires. But what happens when the cache runs out of memory before anything expires? That's where eviction policies come in — they decide which keys get kicked out to make room for new ones. Redis, for example, supports several eviction policies, and picking the right one can dramatically change your cache's behavior under pressure.

The most common algorithms are **LRU** and **LFU**. Some scenarios use random eviction.

### How LRU (Least Recently Used) Works

LRU evicts the key that hasn't been accessed for the longest time. The idea is simple: if you haven't used a piece of data in a while, you probably won't need it soon, so it's the safest thing to throw out.

Imagine a cache with a maximum size of 3 keys. Here's what happens as requests come in:

| Step | Request | Cache State (newest → oldest) | Notes |
|------|---------|-------------------------------|-------|
| 1 | Read A | `[A]` | Cache is empty, so A is added. |
| 2 | Read B | `[B, A]` | B is added. |
| 3 | Read C | `[C, B, A]` | C is added. Cache is now full. |
| 4 | Read A | `[A, C, B]` | A is accessed, so it moves to the front. |
| 5 | Read D | `[D, A, C]` | Cache is full — B is evicted (least recently used). |

Notice what happened in step 4: even though A was the oldest originally, accessing it moved it to the most-recently-used position. So when D came in and something had to be evicted, it was B — the one that hadn't been touched the longest.

LRU is a great default for most general-purpose caches. It works especially well when access patterns follow a temporal pattern — meaning if something was used recently, it's likely to be used again soon. Web page views, API responses, and session data all fit this pattern nicely.

### How LFU (Least Frequently Used) Works

LFU takes a different approach. Instead of looking at *when* a key was last accessed, it looks at *how often* it's been accessed overall. When the cache is full, LFU evicts the key with the lowest access count — the one that's been used the fewest times.

Let's use the same 3-key cache, but this time with LFU:

| Step | Request | Cache State (with access counts) | Notes |
|------|---------|----------------------------------|-------|
| 1 | Read A | `A:1` | A is added, count = 1. |
| 2 | Read B | `A:1, B:1` | B is added. |
| 3 | Read A | `A:2, B:1` | A is accessed again, count = 2. |
| 4 | Read C | `A:2, B:1, C:1` | C is added. Cache is now full. |
| 5 | Read A | `A:3, B:1, C:1` | A accessed again, count = 3. |
| 6 | Read D | `A:3, D:1, C:1` | Cache is full — B is evicted (lowest count, tied with C but came in first). |

Here, A survived even though it wasn't the most recently accessed — it survived because it's been accessed the most times overall. LFU rewards popularity over recency.

LFU shines when some keys are consistently much more popular than others over a long period of time. Think trending products on an ecommerce homepage, top news articles, or frequently searched items. These hot keys deserve to stay in the cache even if they weren't accessed in the last few seconds.

---

Getting TTL and eviction right is what turns a basic cache into a production-grade caching layer. The patterns themselves are simple, but the real skill is in tuning them for your specific workload — and that usually comes from watching your cache hit ratio, miss cost, and memory pressure over time.

---

## Caching Technologies: Picking the Right Tool

Application layer caches are almost always in-memory key-value stores. The two most popular choices are **Memcached** and **Redis**.

Memcached is simple, lightweight, and does one thing well — plain key-value caching. Redis is more powerful, with rich data structures (lists, hashes, sets, sorted sets) and built-in features like pub/sub, persistence, replication, and clustering — useful not just for caching but also for session storage, rate limiting, leaderboards, and queues.

In most modern backend systems, the answer is simple: **start with Redis**. It covers nearly every caching use case, scales well, and gives you room to grow into advanced patterns without switching tools later.

---

## Conclusion

Application layer caching plays a crucial role in building high-performance, scalable, and stable production systems. But to use it well, you need to understand it properly. It's not only about the technical mechanics. You also need to understand the *philosophy* of caching — knowing when to cache, why you're caching, what to cache, and which pattern fits your specific use case. A cache used carelessly can hurt more than it helps. It can serve stale data, hide bugs, or quietly drain memory until things break in production at the worst possible moment.

The honest truth is that caching is never set-and-forget. A production-grade caching layer needs continuous monitoring and tuning. You should always watch the metrics that matter — cache hit and miss ratios, latency, memory usage, and eviction rates — and adjust your TTLs, eviction policies, and key designs based on what the data tells you. A cache hit ratio above 80% is a good sign you're on the right track, and memory management matters just as much, since caches are bounded by the RAM they live in.

If there's one piece of advice I'd leave you with, it's this: **start simple**. Use lazy caching with a sensible TTL, observe how it behaves, and only reach for more complex patterns when you actually need them. Don't cache everything just because you can. Cache thoughtfully, measure constantly, and let real usage guide your decisions.

I hope this 3-part series gives you a solid foundation to build, debug, and reason about application layer caching in your own systems. Caching is one of those tools that looks simple on the surface but reveals more depth the longer you work with it.

---

*Catch up on the rest of the series:*
- *[Part 1: Foundations](#)*
- *[Part 2: Caching Design Patterns](#)*
