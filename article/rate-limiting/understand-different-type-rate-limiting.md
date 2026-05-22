What is rate limiting?
Rate limiting is a technique used to control how many requests a client can perform to api or server within a given time period.




Exp: An API allows only 100 request per minutes per user. if a user exceeds this limit, further requestes are temporarily blocked or delayed to protect the system. also an api allow only 1k request per minutes from all users. so when heavy trafic or all users try to access same time then protect the system using rate limiting.



Why is rate limiting necessary for application and systems?

 It helps prevent a wide range of malicious activities, such as DDoS attacks, brute force attacks, credential stuffing, inventory hoarding attacks, and data scraping, by limiting the number of requests or connections.

Implementing rate limiting can help organizations ensure that resources are available to all users and prevent malicious activity from overwhelming the system.



why use rate limiting:

1. preventing abuse
2. improving performance
3. managing cost/ Cost control
4. ensuring fair usage
5. enchancing security
6. Business tier enforcement — free users get 100 requests/hour, Pro users get 10,000, Enterprise gets unlimited. Rate limiting is how you actually enforce pricing tiers.
7. Compliance with third-party limits — when you integrate with external APIs (Stripe, GitHub, etc.), they enforce their own limits. You rate-limit yourself outbound so you don't get banned.

Use cases: Rate limiting is used in various system or various use cases to control request traffic, prevent abuse and ensure fair and stable use of resource.

API rate limiting:

Web server rate limiting:

Database rate limiting:

Login rate limiting:



Here are some real-world use cases for rate limiting:

Google Maps API – The Google Maps API is a popular tool for developers to integrate maps and location-based services into their applications. However, due to its popularity, the API is a frequent target of malicious traffic, which can overload the service and affect legitimate users. Google Maps API uses rate limiting to protect against these attacks and ensure all users can access the service.
GitHub API – GitHub is a code hosting platform millions of developers worldwide use. The GitHub API provides programmatic access to many platform features, such as creating and managing repositories. Excessive API usage can cause performance issues for the platform and affect other users. GitHub uses rate limiting to prevent these issues and ensure all users can access the API fairly.
Twitter API – The Twitter API allows developers to build applications that interact with the Twitter platform, such as posting tweets or retrieving user data. Abusive or spammy API usage can harm the platform and other users. Twitter uses rate limiting to prevent these issues and ensure all users can access the API without interruption.
Cloudflare – Cloudflare is a popular content delivery network and security service many websites and applications use. Cloudflare uses rate limiting to prevent DDoS attacks and other malicious traffic from overwhelming websites and applications, ensuring their availability and security.



Types:  

1. IP-based rate limiting:  This technique limits the number of requests a client can make based on their IP address within a specific time period. It is commonly used to prevent abuse like bots and denial-of-service attacks.

Exp: An online retailer allows only 10 requests per minute per IP address to prevent bots from scraping product data while allowing normal users to browse smoothly.

pros: 
This approach is widely used due to its simplicity and effectiveness in basic traffic control.

Simple to implement at both network and application levels
Helps block excessive traffic from a single source

cons:

Despite its benefits, it has some limitations in real-world scenarios.

Can be bypassed using VPNs, proxies, or botnets
May block legitimate users sharing the same IP (e.g., corporate networks)


2. Server based rate limiting: This technique limits the number of requests a server can handle within a specific time period to prevent overload and maintain performance.

Exp: A music streaming service allows only 100 requests per second per server to ensure the system remains fast and responsive during peak usage.

Pros:

This approach helps maintain system stability by controlling traffic at the server level.

Protects servers from being overwhelmed during high traffic
Ensures fair resource usage so no single user degrades performance

Cons:

However, it may not be fully effective in distributed environments.

Can be bypassed if requests are spread across multiple servers
Legitimate users may face delays if limits are too strict or traffic is high


3. Geography-based rate limiting: This technique limits requests based on the geographic location of the user’s IP address. It is useful for controlling traffic from specific regions and improving security or compliance.

Exp: A social media platform limits requests from a region known for bot activity to 10 requests per minute to reduce spam and fake accounts.


Pros:

This approach is helpful for controlling region-specific traffic and improving security.

Helps reduce malicious traffic from high-risk regions
Assists in complying with regional laws and regulations

Cons:

However, it may affect legitimate users and can be bypassed.

Can be bypassed using VPNs or proxy servers
May block genuine users traveling or using international networks


4. Specific user id based rate limiting: 
User-based rate limiting is another method that restricts access based on the user account making the request. It can help prevent credential stuffing attacks, but it requires identifying unique users across different sessions, which can be challenging.





Rete Limiting Algorithms:


1. Token Bucket Algorithm:

Description: Uses tokens to control traffic flow. Tokens are added to a bucket at a regular rate and requests consume tokens. If the bucket runs out of tokens, new requests are denied.
Example: A bucket can hold 10 tokens and 1 token is added every 10 seconds. A request needs 1 token to pass. If there's a sudden burst of 15 requests, only 10 can go through, and subsequent requests must wait for new tokens.

Example: We get 5 tokens per minute.

If you don’t use them, they get saved (up to a limit)
Suddenly you send 5 requests - all allowed (burst allowed)
6th request - blocked (no tokens left)


2. Leaky Bucket Algorithm:

Description: Requests are added to a queue (bucket) and processed at a fixed rate to smooth out burst traffic.
Example: If the bucket size is 10 and the rate is 1 request per second, and a burst of 20 requests comes in, the first 10 are queued and processed at 1 per second, while the rest are either queued (if the bucket can hold them) or discarded.

Example: Bucket can hold 5 requests, and processes 1 request per second

If 5 requests come - all stored and processed slowly
If 10 requests come - 5 stored, 5 rejected (overflow)

3. Fixed Window Countirng Algorithm:

Description: Divides time into fixed windows and counts the number of requests in each window.
Example: If the limit is 100 requests per hour, and a user makes 100 requests in the first half-hour, they will be blocked for the remaining half-hour, even if the server is underutilized during that time.

Example: Limit = 5 requests per minute

User sends 5 requests at 10:00–10:00:50 - Allowed
Sends 2 more requests at 10:00:55 - Blocked
At 10:01:00 - Counter resets - Requests allowed again

4. Sliding Window Log Algorithm:

Description: Keeps a time-stamped log of requests. It checks whether adding a new request would exceed the rate limit, considering the time frame.
Example: If the limit is 100 requests per hour, each incoming request is checked against the log of requests in the past hour. Older entries are discarded.

Example: Limit = 5 requests per minute

User sends 5 requests between 10:00:00 – 10:00:40 - Allowed
At 10:00:50, user sends 1 more request - Blocked (already 5 in last 60 sec)
At 10:01:10, old requests (before 10:00:10) expire - New request - Allowed


5. Sliding window counter:
Description: A hybrid of the fixed window and the sliding log, offering a balance between efficiency and precision. It combines the fixed window's simplicity and the sliding log's accuracy.
Example: If the limit is 100 requests per hour, the server counts requests in the current window and a fraction of the requests from the previous window, based on the time elapsed.



Rate limiting can be in client side, server side:


Ret limiting Implementing challenges:

Latency, false positives, configuration complexity, scalability challenges.