Reference Articles:
1. https://aws.amazon.com/caching/best-practices/
3. https://learn.microsoft.com/en-us/azure/architecture/best-practices/caching
4. https://altersquare.medium.com/best-practices-for-application-level-caching-d3e6ab2b4822
5. https://dev.to/budiwidhiyanto/caching-strategies-across-application-layers-building-faster-more-scalable-products-h08
6. https://www.linkedin.com/pulse/caching-strategies-101-how-leverage-caches-system-design-qjhac/
7. https://www.geeksforgeeks.org/system-design/caching-system-design-concept-for-beginners/
8. https://www.geeksforgeeks.org/system-design/redis-cache/






LRU and LFU need to explain


Browser caching -> CDN Caching -> API Gateway caching -> Application Layer Caching -> Database Caching

# Application Layer Caching

In my 6 years of backend engineering writing countless APIs, handling numerous services, and constantly optimizing response times and performance one tool has consistently proven indispensable across every project: caching. I've used caching at many different layers to squeeze out better performance, but in this article, I want to focus specifically on application layer caching.

In this modern era of software engineering, users and consumers demand speed. They want to see search results instantly, load their dashboards without delay, and interact with applications that feel snappy and responsive. Time is literally cost in this industry every extra millisecond of latency translates to lost engagement, lost conversions, and ultimately lost revenue. The success of any software product today heavily depends on how quickly it can deliver results to its users.

Let's understand this with a simple example. Suppose a user wants to view their profile on a web application. To fetch that profile data, the request has to travel through multiple layers from the browser, across the network, through load balancers, API gateways, application servers, and finally to the database. Now imagine the same user requesting the same data multiple times. If that request travels the same long distance on every single call, it becomes expensive in terms of both time and resources, and the application simply cannot be fast. This is exactly the problem caching solves.

At its core, a cache is a mechanism for faster access to frequently requested data. Most caches live in memory (RAM), which is blazingly fast compared to disk based storage or network calls to remote services. Instead of recomputing a result or fetching it from a slow source repeatedly, we store it once in a cache and serve subsequent requests directly from there.

Without caching, modern software would struggle to scale. Today's applications serve millions of concurrent users, handle massive traffic spikes, and are expected to respond in milliseconds something that would be nearly impossible if every request had to hit the database or recompute expensive operations from scratch. In a microservices architecture, caching is not just an optimization but a necessity services communicate over the network, and without caching, inter service calls can quickly become a bottleneck that brings the entire system down under load. Even in a monolithic architecture, caching is widely used to reduce database pressure, improve response times, and handle concurrent requests efficiently.

Caching can be applied at many different layers of the stack. When a client makes a request, it travels through several stages, and each stage offers an opportunity to cache:

Browser cache — stores static assets and API responses on the client side, avoiding network calls entirely.
CDN cache — serves static content (images, scripts, stylesheets) from edge locations closest to the user.
API Gateway cache — caches responses at the gateway level, reducing load on backend services.
Application layer cache — stores computed results, session data, and frequently accessed objects in memory within the application itself.
Database cache — caches query results and frequently accessed rows to reduce disk I/O.

Each layer has its own trade-offs, use cases, and challenges. However, in this article, I'll focus exclusively on the application layer cache the layer where, in my experience, backend engineers have the most control and where thoughtful caching decisions can deliver the biggest performance gains.




What is caching?

Caching is a common technique that aims to improve the performance and scalability of a system. It caches data by temporarily copying frequently accessed data to fast storage that's located close to the application. If this fast data storage is located closer to the application than the original source, then caching can significantly improve response times for client applications by serving data more quickly.

Caching is most effective when a client instance repeatedly reads the same data, especially if all the following conditions apply to the original data store:

It remains relatively static.
It's slow compared to the speed of the cache.
It's subject to a high level of contention.
It's far enough away from clients that network latency is significant.


caching in distributed application: in distributed application typically caching use these stategis:
They use a private cache, where data is held locally on the computer that's running an instance of an application or service.
They use a shared cache, serving as a common source that multiple processes and machines can access.

In both cases, caching can be performed client-side and server-side. Client-side caching is done by the process that provides the user interface for a system, such as a web browser or desktop application. Server-side caching is done by the process that provides the business services that are running remotely.


private caching: private cache is a most basic type of cache is an in memory store in a computer or virtual computer where application run. this type of cache is quick to access. the size of a cache is typically constraind by the amount of memory available on the machine that hosts the process.

private caching, where each application instance maintains its own local cache. The key points: in-memory caches are the fastest option but limited by available RAM. When data exceeds memory capacity, you can fall back to local file storage — slower than memory but still faster than network calls. The trade-off with private caches is consistency: since each instance holds its own copy, concurrent instances can end up with different snapshots of the data, meaning identical queries might return different results across instances.

figure or diagram for private cache:


shared caching: Shared caching solves the consistency problem of private caches by storing data in a single, separate location — typically an external service. This way, all application instances see the same cached data, eliminating stale or mismatched results across instances.
The big advantage is scalability: shared caches often run on server clusters that distribute data transparently, and you can scale simply by adding more servers to the cluster.
The two downsides are slower access (since the cache is no longer local to the application) and added complexity from having to set up and maintain a separate cache service.

figure or diagram for shared cache:


Cache Architecture: What to Consider Before You Build:

When to cache? → Cache data that's read frequently but rarely modified. Never rely on cache as the only store for critical data.
How to load? → Use lazy loading (on first request) or seed at startup. Works best for static data, partial entities, and expensive computations.
Dynamic data? → If the data changes fast and isn't critical, store it directly in cache and skip the persistent database.
Expiration? → Use absolute or sliding TTL to prevent stale data. When cache is full, eviction removes items using LRU, FIFO, MRU, or event-based policies.
Client staleness? → Services can't control client caches directly. Change the resource URI to force clients to fetch the latest version.
Concurrency? → Optimistic approach checks if data changed before writing — good for rare collisions. Pessimistic approach locks data during updates — use only for short, collision-prone operations.
Availability & scale? → Always fall back to the original data store if cache goes down. Use local + shared cache layers together. Scale out with sharding, clustering, and replication.
Consistency? → Distributed caches like Redis prioritize availability over strong consistency. Use short TTLs or bypass cache entirely for data that must always be current.
Security? → Authenticate who can read/write, partition or encrypt data subsets for access control, and use SSL/TLS over public networks.



Without chaching problems faces and problems solve with caching?
Faster user interactions. Caching frequently accessed data can reduce API response times by 50-95%, making applications feel more responsive. A mobile app reduced its average API response time from 300ms to just 35ms after implementing application caching.

Lower infrastructure costs. Optimized caching reduces CPU and memory usage, allowing teams to handle more traffic with fewer resources. A B2B platform reduced its server count by 60% while handling more requests.

Reduced database load. Caching minimizes expensive database queries, keeping systems stable under heavy traffic. An analytics dashboard lowered database CPU utilization from 85% to 30%, eliminating timeouts during peak hours.

Better scalability without extra cost. Caching allows systems to handle traffic spikes without requiring a massive increase in infrastructure. As one CTO put it, "Before caching, each new marketing campaign meant an emergency infrastructure meeting. Now we just watch the metrics and smile, knowing the system will handle it."


Application Layer caching pitfalls:

Cache invalidation challenges. Knowing when to refresh or discard cached data is surprisingly complex. Some engineering teams have created cache invalidation diagrams that look more like abstract art than structured designs.

Stale data issues. If cache invalidation isn’t handled correctly, users may see outdated information. A marketplace app once displayed "In Stock" labels for products that had already sold out, frustrating customers and increasing support tickets.

Cache penetration. If non-existent data is frequently requested, it can bypass the cache and overload the database. A system experiencing slowdowns due to bots requesting random product IDs mitigated the issue by implementing a "negative result cache" to remember which IDs didn’t exist.

Cache avalanche. If many cached items expire simultaneously, the sudden surge of database queries can cause system failure. A social platform crashed during a product launch when all promotional content caches expired simultaneously, triggering thousands of database queries.

Local vs. distributed caching challenges. Local in-memory caches work well for small applications, but as traffic grows, a distributed caching system becomes essential. A startup struggling with inconsistent user experiences found that switching to Redis as a centralized cache immediately resolved the issue.


deciding whether to cache:

Is it safe to use a cached value? The same piece of data can have different consistency requirements in different contexts. For example, during online checkout, you need the authoritative price of an item, so caching might not be appropriate. On other pages, however, the price might be a few minutes out of date without a negative impact on users.

Is caching effective for that data? Some applications generate access patterns that are not suitable for caching—for example, sweeping through the key space of a large dataset that is changing frequently. In this case, keeping the cache up to date could offset any advantage caching could offer.

Is the data structured well for caching? Simply caching a database record can often be enough to offer significant performance advantages. However, other times, data is best cached in a format that combines multiple records together. Because caches are simple key-value stores, you might also need to cache a data record in multiple different formats, so you can access it by different attributes in the record.


Data caching stores frequently accessed information like user profiles or API responses to reduce database load, making it ideal for content that’s accessed often but doesn’t change frequently.
Computation caching saves results of heavy computations such as analytics reports to avoid repeated processing, particularly valuable for resource-intensive calculations and data aggregations.
Distributed caching uses multiple servers for shared caching in high-traffic, multi-server setups, ensuring consistent and synchronized data access as applications scale horizontally.

Caching Types:
Data caching stores frequently read, rarely changed data (like product listings) in memory to avoid repeated database hits. You set different TTLs based on how volatile the data is.
Computation caching stores the results of expensive operations — aggregations, ML predictions, report generation — so you don't re-run heavy calculations for the same inputs.
Distributed caching shares cache across multiple servers (Redis Cluster, Memcached) so horizontally scaled apps all read from the same cache layer. The main challenge is keeping data consistent across nodes, which you handle with patterns like pub/sub invalidation or versioned keys.

Session caching. Storing user session data in memory for quick access. This ensures that applications can efficiently maintain user authentication, preferences, and shopping cart data across multiple requests or page reloads without frequent database lookups.

Rate limiting. Using a cache to track and limit API requests from individual users. This helps prevent accidental or intentional overload of the system by enforcing request thresholds while reducing unnecessary processing.







caching design patterns:

Lazy caching(cache aside): what is lazy caching?

workflow of lazy caching:
Your app receives a query for data, for example the top 10 most recent news stories.

Your app checks the cache to see if the object is in cache.

If so (a cache hit), the cached object is returned, and the call flow ends.

If not (a cache miss), then the database is queried for the object. The cache is populated, and the object is returned.

when use lazy caching: You should apply a lazy caching strategy anywhere in your app where you have data that is going to be read often, but written infrequently. In a typical web or mobile app, for example, a user's profile rarely changes, but is accessed throughout the app. A person might only update his or her profile a few times a year, but the profile might be accessed dozens or hundreds of times a day, depending on the user. 


pros: This method is memory-efficient since only requested data is cached.


cons: However, it can lead to higher latency on the first request and requires explicit invalidation logic. A common issue in high-traffic systems is multiple requests simultaneously missing the cache for the same key, causing redundant database queries. Techniques like distributed locks or atomic operations can manage cache updates and prevent stale data from being re-cached.



Write Through: Every time data is updated, it’s written to both the cache and the backend database simultaneously. This ensures the cache is always in sync with the latest data but adds some latency to write operations. A ticket-booking platform used this approach to ensure seat availability information was always accurate.

what is write through?

Workflow of write through:

when use write trhough:

pros:

cons:



hybrid(lazy caching + write through):



Read Through: The cache itself is responsible for retrieving missing data. If the requested data isn’t in the cache, it automatically fetches it from the source. This simplifies application logic but requires a more sophisticated caching layer.

what is read through?

Workflow of read through:

when use read trhough:

pros:

cons:




Write Behind: 

what is Write Behind?

Workflow of Write Behind:

when use Write Behind:

pros:

cons:


Time to live:

what is time to live? TTL (Time-to-Live) and expiration policies automatically refresh or remove cached data after a set time, reducing the risk of serving outdated information. Setting a 10-minute TTL for product inventory data ensures regular updates, keeping stock levels accurate without manual intervention.

The ideal TTL depends on data volatility, acceptable staleness, system performance, and the cost of cache misses. Dynamic data like real-time pricing benefits from shorter TTLs, while static content such as country codes can have longer TTLs. Layered caching architectures can implement TTL hierarchies where browsers and CDNs use shorter TTLs while database-level caches use longer ones, balancing freshness and efficiency across the system.

Monitoring cache hit/miss ratios and user feedback helps refine TTL settings. Systems with well-tuned TTLs often achieve cache hit rates above 80%, indicating effective configuration. When precise data consistency is critical, versioned cache keys provide a more reliable choice.

strategis of time to live:
Always apply a time to live (TTL) to all of your cache keys, except those you are updating by write-through caching. You can use a long time, say hours or even days. This approach catches application bugs, where you forget to update or delete a given cache key when updating the underlying record. Eventually, the cache key will auto-expire and get refreshed.

For rapidly changing data such as comments, leaderboards, or activity streams, rather than adding write-through caching or complex expiration logic, just set a short TTL of a few seconds. If you have a database query that is getting hammered in production, it's just a few lines of code to add a cache key with a 5 second TTL around the query. This code can be a wonderful Band-Aid to keep your application up and running while you evaluate more elegant solutions.

A newer pattern, Russian doll caching, has come out of work done by the Ruby on Rails team. In this pattern, nested records are managed with their own cache keys, and then the top-level resource is a collection of those cache keys. Say you have a news webpage that contains users, stories, and comments. In this approach, each of those is its own cache key, and the page queries each of those keys respectively.

When in doubt, just delete a cache key if you're not sure whether it's affected by a given database update or not. Your lazy caching foundation will refresh the key when needed. In the meantime, your database will be no worse off than it was without caching.




russian doll caching:


Evicitions: what is eviction?

eviction policies: 
allkeys-lfu: The cache evicts the least frequently used (LFU) keys regardless of TTL set
allkeys-lru: The cache evicts the least recently used (LRU) regardless of TTL set
volatile-lfu: The cache evicts the least frequently used (LFU) keys from those that have a TTL set
volatile-lru: The cache evicts the least recently used (LRU) from those that have a TTL set
volatile-ttl: The cache evicts the keys with shortest TTL set
volatile-random: The cache randomly evicts keys with a TTL set
allkeys-random: The cache randomly evicts keys regardless of TTL set
no-eviction: The cache doesn’t evict keys at all. This blocks future writes until memory frees up.

A good strategy in selecting an appropriate eviction policy is to consider the data stored in your cluster and the outcome of keys being evicted.
Generally, LRU based policies are more common for basic caching use-cases, but depending on your objectives, you may want to leverage a TTL or Random based eviction policy if that better suits your requirements.




The thundering herd:
Also known as dog piling, the thundering herd effect is what happens when many different application processes simultaneously request a cache key, get a cache miss, and then each hits the same database query in parallel. The more expensive this query is, the bigger impact it has on the database. If the query involved is a top 10 query that requires ranking a large dataset, the impact can be a significant hit.


caching technologies:
in memory key-value category of NoSQL database.
popular in memory key value stores are Memecached and Redis




Versioned Cache Keys Strategy:

Versioned cache keys include a version identifier — like a timestamp, hash, or incrementing number — within the cache key itself. When data changes, a new key is generated, making old cache entries obsolete. In a content management system, an article might be cached using its last modified timestamp (e.g., “article:456:20251018T0100”). Editing the article updates the timestamp, creating a new cache key that guarantees users always see the latest version without requiring manual cache purging.

This approach is particularly useful in distributed systems where coordinating cache invalidation across multiple nodes can be challenging. Instead of clearing caches across nodes, each node simply starts using the new versioned key, effectively bypassing outdated entries. However, managing versioned keys can be complex as applications need to track versions and handle memory occupied by old cache entries until they’re evicted





Selecting Caching Tools
Choosing the right caching tool requires careful consideration of data volatility, system architecture, performance goals, and workload type. Applications with frequently changing data need tools that excel at invalidation strategies, while high-traffic systems benefit from distributed caching solutions.

Tools: private cache(in memory), shared cache(redis,memecached)



Configuration Best Practices
To get the most out of your caching setup, proper configuration is essential. Allocate enough memory, monitor hit ratios (aim for over 80%), and set eviction policies like LRU (Least Recently Used) or LFU (Least Frequently Used) based on your data access patterns.

When configuring TTL settings, strike a balance between data freshness and performance. Use longer TTLs for static data like country codes or product categories, and shorter TTLs for dynamic content such as inventory levels or user preferences. AWS reports that effective caching can cut database load by up to 80% and improve application response times by up to 10x.

Security is another critical consideration. Limit network access to cache servers, enable authentication and encryption (e.g., TLS for Redis), and avoid caching sensitive data unless absolutely necessary. Regular updates and patches are essential to minimize vulnerabilities.


Monitoring and optimization
Performance metrics
Memory Management
Continues Optimization