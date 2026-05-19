# Production-Grade REST API: What 6 Years in Production Taught Me

In my **6 years of building REST APIs** and running them in production with real consumers, I've learned one hard truth: **building an API is easy, but building one that survives production is a completely different game**. Many developers know how to make an API work and assume that's enough. But making it work and making it work reliably **at scale** are two very different things. This article is a short, practical checklist of the best practices I follow to ship REST APIs that don't break under real users.

## API, REST, and RESTful: the quick distinction

An **API (Application Programming Interface)** is a **contract between two pieces of software** that defines how they communicate, like a restaurant menu. **REST** is **not a tool or protocol**; it's an **architectural style**, a set of principles (**stateless**, **resource-oriented**, **standard HTTP methods**, **standard representations like JSON**). A **RESTful API** is simply an API that follows REST principles. You can't "install" REST, you **design** for it.

## Best practices checklist

### Use nouns, not verbs in endpoints

**Endpoints represent resources; HTTP methods represent actions.** So URLs should be **nouns, plural, and predictable**.

```
GET    /articles
POST   /articles
PATCH  /articles/123
DELETE /articles/123
```

Avoid `/getArticles` or `/deleteArticles/123`, the method already carries the verb. For **non-CRUD actions** like password resets, **model the action as a resource**: `POST /password-resets`. Keep **nesting to two levels max**, deeper usually signals a modeling problem.

```
do:    GET /users/123/articles
don't: GET /users/123/articles/456/comments/789
```

### Use the correct HTTP methods (and understand idempotency)

**Idempotent** means calling the same request multiple times produces the **same state**, like pressing a paid order button five times but only being charged once. **GET, PUT, PATCH, and DELETE should be idempotent. POST is not idempotent** because each call creates a new resource (call it twice, get two records). Use **GET for reads**, **POST to create**, **PUT to fully replace**, **PATCH for partial updates**, and **DELETE to remove**. From my experience, getting idempotency right on POST prevents most **duplicate-charge and double-write bugs** in production. The common way is the client sends a unique **`Idempotency-Key`** value in the **request header**, and the server stores it so repeat calls with the same key return the original result instead of creating a new record.

### Return meaningful HTTP status codes

**Let the status code tell the outcome and let the body tell the detail.** I've seen teams return `200 OK` with an error inside the body, and clients silently treated failures as successes. Stick to the mental model: **2xx success, 4xx client error, 5xx server error**.

Two pairs that confuse most engineers:

- **`401 Unauthorized`** (not authenticated) vs **`403 Forbidden`** (authenticated but not allowed)
- **`400 Bad Request`** (malformed request) vs **`422 Unprocessable Entity`** (valid format, failed business validation)

Getting these right will already put your API ahead of most production systems I've reviewed.

### Standardize success and error responses

If every endpoint returns a **different JSON structure**, clients write custom handling for every response. This breaks **DRY (Don't Repeat Yourself)**, adds unnecessary code, and creates bugs. **Pick one response structure** that's easy for both client and backend, and **enforce it across every service**.

```json
// success
{ "success": true, "data": { "id": 101, "name": "Rabbi Hasan" }, "message": "User fetched successfully" }

// error
{
  "success": false,
  "error": { "code": "USER_NOT_FOUND", "message": "No user exists with the given ID", "details": { "user_id": 101 } }
}
```

For **multi-field validation failures**, return `errors` as a **list**. The exact shape doesn't matter, **consistency does**.

### Validate input and output, both are mandatory

You never know what a real user will send. **Garbage data, oversized payloads, SQL injection attempts**, they all hit production. **Validate every input** before it reaches your database. **Frontend validation alone is never enough**; an API can be called without any frontend.

**Output validation** matters just as much. If a client only needs 3 of 10 attributes, returning all 10 **wastes bandwidth, increases response time, and degrades user experience at scale**. **Return only what's needed**, with the **correct types**. Short attribute names also help.

### Pagination, filtering, and sorting

Imagine `GET /products` returning **10,000 rows**. The database stalls, the API freezes, the client freezes. **Pagination fixes this.** Before choosing a strategy, you must understand **how each one actually works at the query and database level**, how **offsets scan rows**, how **cursors use indexes**, how **keyset uses the last seen value**. Once you know that, pick the pattern that fits your data size and access pattern. The common ones are **offset-based, page-based, cursor-based, keyset/seek, and time-based**. From my experience, **cursor or keyset pagination scales much better than offset** once you cross a few hundred thousand rows.

### Security is non-negotiable

A REST API is a **door to your server**. **Design security from day one**, not later.

**HTTPS**: Always **encrypt traffic with SSL/TLS**. There is no valid reason to run a production API over plain HTTP.

**API keys**: Use for **server-to-server access**. **Never embed them in frontend code**, they'll be scraped and abused.

**OAuth 2.0 bearer tokens**: Handles both **authentication** (who is this user?) and **authorization** (what can they do?). Essential whenever users access **scoped data**.

**CORS**: **Explicitly list allowed origins** for private APIs. **Wildcards are convenient but weaken security**.

**Rate limiting and throttling**: **Rate limiting** caps how many requests a client can make in a time window (e.g. **100 requests per minute**) and **blocks** the rest. **Throttling** **slows requests down** instead of blocking them outright. Both protect your API from **brute-force attacks, scraping, accidental client loops, and traffic spikes** that can take down the whole service.

### Caching

In production, **the fastest request is the one you never make**. What this means is simple, if you can **serve a response from cache** instead of re-running the database query and business logic every time, the request finishes in **milliseconds** and barely touches your server. **Caching reduces database load, cuts latency, and saves cost**, but it's not just "stick Redis in front of the DB." You have to think about **cache layers (CDN, gateway, application, database)**, **invalidation strategy**, **stampedes**, and **consistency**. Done wrong, caching serves **stale data** and creates bugs that are nearly impossible to reproduce. For a deeper dive into how application-layer caching actually works in production, read my full guide: [The Complete Guide to Application-Layer Caching, Part 1](https://medium.com/@jasrabbi50/the-complete-guide-to-application-layer-caching-part-1-why-caching-is-not-just-a-key-value-store-e569f4167532).

### Versioning

**Change is constant.** Schemas evolve, fields get renamed, auth changes. **Any breaking change should ship under a new version** so existing clients don't break overnight. **Non-breaking additions** (a new optional field) don't need a new version. I default to **URL path versioning**, `/api/v1/users`, because it's **explicit, easy to route, and trivial to test in a browser**. **Plan versioning from day one**; adding it later to an API that already has live clients is painful.

### Documentation

Without documentation, your API is a **black box**, backend and frontend teams burn hours in Slack just to clarify what an endpoint does. **Treat documentation as infrastructure, not a chore.** Use **OpenAPI** with **Swagger** or **Redoc** so docs are **generated from your schema and stay in sync with code**. The moment documentation becomes a separate manual task, it starts decaying, and **outdated docs are often worse than none**.

### Observability, beyond monitoring

From my experience, **observability is the single most important thing in a production server**. **Monitoring is a smoke alarm**: it tells you something is wrong. **Observability is the full security system**: it tells you **what broke, where, and why**. The **four pillars** are **metrics, events, logs, and traces**, and you need all four. Use **structured JSON logs**, **distributed tracing across services**, and **correlate signals together**. The standard stack I use is **OpenTelemetry, Prometheus, Loki, and Grafana**: **instrument once, collect everywhere, visualize in one place**. The incidents that hurt most are the ones monitoring was never designed to catch, **observability instruments for the unknown**.

### Conclusion

**Production-ready is not a feature you add on at the end.** It's a **discipline** applied to every endpoint, every response, every deploy. Get these basics right, **naming, methods, status codes, validation, security, caching, versioning, docs, observability**, and your API will survive **real users, real traffic, and real failures**.
