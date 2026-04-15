1. What is api and rest api?
2. why do we need rest api? what problem solve rest api?
2. Methods of rest api. need to know when which method use for which apis
3. rest api endpoint use nouns and meaningfull endpoint
4. implement prooper http status code for different scinario. for this need to knwo basic status code when which use
5. standarise success and error response. and try to main tain same json structure for succes and error
6. input and output validation is mandatory. why input validation need and why output validation needs
7. api versioning and when change version need to know
8. filtering,sorting,pagination when and how use
9. security for api is mandatory
10. proper documentation is also mandatory
11. based on application and requirment api security and access contor
12. monitor api logs and also monitor api performance

Request header
Response Header



reference links:
https://stackoverflow.blog/2020/03/02/best-practices-for-rest-api-design/
https://blog.postman.com/rest-api-best-practices/
https://www.ibm.com/think/topics/rest-apis
https://oneuptime.com/blog/post/2026-02-20-api-design-rest-best-practices/view
https://stackoverflow.blog/2021/10/06/best-practices-for-authentication-and-authorization-for-rest-apis/



What is api?
API full form is applicaton programming interface. An easy way api is make communication between two peach of code or software or server or function etc. 

An API is a contract between two pieces of software that defines how they communicate. Think of it like a restaurant menu — it tells you what you can order (the available operations) and what you'll get back, without needing to know how the kitchen works.
Any mechanism for software-to-software communication counts: a Python library's functions, a database driver, an operating system's system calls — these are all APIs.
Example: Python's os module is an API. You call os.listdir("/home") and get a list of files. You don't need to know how the OS retrieves that list internally.


what is rest?
rest is not a tool or any protocol or any software. rest is a set of rules. its a philosophy.

REST is an architectural style — a set of constraints/principles for designing networked applications. It's not code or a tool; it's a philosophy. The key principles are: use standard HTTP methods(get,post,put,patch,delete), be stateless (each request is self-contained), organize things around resources identified by URLs, and use standard representations like JSON.
REST is an idea, not an implementation. You can't "install" REST.


what is restfull api?
api and rest combine make restfull api. when any api follow rest rules or philosophy then we can call it restfull api.



A REST API is an application programming interface architecture style that conforms to specific architectural constraints, like stateless communication and cacheable data. It is not a protocol or standard. While REST APIs can be accessed through a number of communication protocols, most commonly, they are called over HTTPS, so the guidelines below apply to REST API endpoints that will be called over the internet.



why do we need rest api? what problem solve rest api?
now we must need to know why and when do i use rest api instead api or others things. for better best productiion grade rest api this need to know mandatory. also what problems solve it.


Best practice of rest api?

1. use noune not verbs in end point: REST API endpoints always represent resources, and methods represent actions. So for endpoints, we use nouns, while methods are already actions. You should use nouns that represent the entity you are retrieving, manipulating, or deleting as the pathname. Endpoints represent entities meaning most of the time, we create, retrieve, update, or delete some entity from a database, like users, articles, posts, products, or orders. Since HTTP methods already describe the actions, your URLs should focus on what you are working with. Also, use plural nouns for collections and follow consistent patterns throughout your API. Developers should be able to predict what an endpoint does and returns based on endpoint names and patterns they have already seen.

do: 
    GET /articles
    POST /articles
    PUT /articles/123
    PATCH /articles/123
    DELETE /articles/123
don't:
    GET /getArticles
    POST /create_articles
    PUT /update-articles/123
    PATCH /updateArticles/123
    DELETE /deleteArticles//123

For relationships, you can use nested resources that reflect relationships in the URL structure, but remember not to go too deep things get unwieldy and messy. In production, more than two levels of nesting often signals a resource modeling problem. In such cases, consider flattening the structure or introducing a dedicated endpoint.

do:
GET /users/123/articles 

don't:
GET /user/123/articles/123/comments

However, in real production systems, not every operation is simple CRUD. Actions like resetting a password, verifying an OTP, or sending a verification email etc.don't map cleanly to a resource. In these cases,
Model the Action as a Resource (Most RESTful): Reframe the verb as a noun. Instead of thinking "reset the password," think "create a password reset request." This keeps your API consistent with REST conventions.

DO: 
POST /password-resets
POST /email-verifications
POST /otp-verifications


2. use correct http methods: HTTP methods define the action being performed. Using them correctly makes your API predictable and allows clients to understand what each request will do.
    GET retrieves data: Use GET for read-only operations that don’t modify server state. GET requests should be safe to call repeatedly without side effects.GET requests are cacheable and can include query parameters for filtering, sorting, and pagination. Never use GET for operations that change data. But some scenario using GET request can update some column value when retrive something like you want to view count of eavrytime someone see details of product or post or articles.

    POST creates new resources: Use POST when creating new resources or triggering actions that change server state. The server typically assigns the new resource’s identifier.

    PUT updates or replaces resources: Use PUT for full updates of existing resources. PUT is idempotent, meaning multiple identical requests produce the same result.

    PATCH makes partial updates: Use PATCH when you only need to modify specific fields without sending the entire resource. PATCH is particularly useful for large resources where sending the complete object would be inefficient.

    DELETE removes resources: Use DELETE to remove resources from the server. Like PUT, DELETE should be idempotent.


3. input and output validation must need

4. common respone pattern for success and errors

5. return meaningfull status code

6. use proper security

7. Caching

8. Rate limiting

9. Versioning

10. Need proper testing

11. Provide comprehensive documentation

12. Observe log, monitor api usages

