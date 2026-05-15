 what is graphql?


 rest api disadvantage:
 1. multiple endpoints. in graphql use single endpoin
 2. over fetching data. in graphql only needed data can fetch. also can fetch nested related data easily. with single query
 3. under fetching data. in graphql only needed data can fetch easily. also can fetch nested related data easily. with single query



graphql Query basics:

query ReviewsQuery {
    reviews {
        rating
    }
}


graphql mutations:



graphql 5 scaler types: int, float, string, boolean, ID

schema and types

what is specila Query types in graphql




resolver functions: 

graphql related data


graphql mutations(any kind of change in data like add,update,delete)












Graphql introduction:

new api standard that was invented & open sourced by facebook.
it enables declaratative data fetching.
graphql server exposes single endpoint and responds to queries



why graphql over rest?

1. ovrfething: get unnecessary data. in graphql solve this get unnecesary data problem
2. userfetching: and endpoin doesn't return enough of the right information, need to send multiple requests (n+1 request problem). graphql a solve this with one endpoint and one request.

3. in rest, structure endpoints according to clients data need. so when any new requirements and design change then need to adjust in api.. but graphql no need to adjust api when product requirements and design changes

4. in graphql faster feedback cycles and product iterations

5. in graphql clients only fetch exactly what data is need. fine grained info about what data is read by clients

6. in graphql enables evolving api and deprecating unneeded api features
7. in graphql greate opportunities for instrumenting and performance monitoring

8. graphql uses strong type system to define capabilites of an api. schema serves as contract between client and server. frontend and backend team can work completely independent from each other



graphql core concept:

1. schema

2. query

3. mutation

4. subscriptions


root types schema: 
type Query {} 
type Mutation {}  
type subscription {}




graphql architecture:

architectural use cases:
1. graphql server with a connected database
2. graphql server to integrate existing system
3. a hybrid approch with a connected database and integration of existing system


use case 1: graphql server with a connected database:

1. often used for greenfield projects
2. uses single web server that implements graphql
3. server resolves queries and constructs response with data that it fetches from tha database(sql or nosql)

use case 2: graphql server to integrate existing system:

1. compelling use case for companies with legacy infrastructures and many different apis
2. graphql can be used to unify existing systems and hide complexity of data fetching logic
3. the server doesn't care about the what the data sources are(databases, web services, 3rd party apis..)


use case 3: a hybrid approch with a connected database and integration of existing system:


how graphql fit with these 3 use cases? 

with resolver functions:

1. graphql queries/mutations consist of set of fields
2. graphql server has one resolver function per field
3. the purpose of each resolver is to retrieve the data for its corresponding field.


graphql clients:

1. graphql is great for frontend developers as data fetching complexity can be pushed to the server side
2. client doesn't care where data is coming from
3. opportunity for ew abstractions on the frontend



Let’s consider the major change that’s introduced with GraphQL in going from a rather imperative data fetching approach to a purely declarative oneWhen fetching data from a REST API, most applications will have to go through the following steps:

construct and send HTTP request (e.g. with fetch in Javascript)
receive and parse server response
store data locally (either simply in memory or persistent)
display data in the UI


With the ideal declarative data fetching approach, a client shouldn’t be doing more than the following two steps:

describe data requirements
display data in UI







what is fragment in graphql?

use parameterizing fields with arguments

named query results with aliases


in graphql has two types of data:

scalar types: string, int, float, boolean, id
object types: any object like User/Post

also in graphql you can use enums in schema

graphql has interface: 

graphql  has union types



some tools:

introspection: The designers of the schema already know what the schema looks like but how can clients discover what is accessible through a GraphQL API? We can ask GraphQL for this information by querying the __schema meta-field, which is always available on the root type of a Query per the spec.

GraphQL Playground
GraphQL Playground is a powerful “GraphQL IDE” for interactively working with a GraphQL API. It features an editor for GraphQL queries, mutations and subscriptions, equipped with autocompletion and validation as well as a documentation explorer to quickly visualize the structure of a schema (powered by introspection). It also can display your query history or lets you work with multiple GraphQL APIs side-by-side. It also seamlessly integrates with graphql-config.

It is an incredibly powerful tool for development. It allows you to debug and try queries on a GraphQL server without having to write plain GraphQL queries over curl, for example.

Prisma Pulse
Prisma Pulse enables you to easily implement GraphQL subscriptions or live queries with real-time updates from the database in a robust, scalable and type-safe way.

It is compatible with all popular libraries from the GraphQL ecosystem, such as Apollo Server and GraphQL Yoga.

Prisma Accelerate
Prisma Accelerate is a global database cache with a scalable connection pool that can help speed up your database queries.

It’s especially useful when you’re deploying your GraphQL API in a serverless environment where a lot of traffic may quickly exhaust your database connection limit. Accelerate’s edge caching further ensures that your resolvers can return data faster because they don’t need to fetch the data all the way from the database.



security in graphql: Since clients have the possibility to craft very complex queries, our servers must be ready to handle them properly. These queries may be abusive queries from evil clients, or may simply be very large queries used by legitimate clients. In both of these cases, the client can potentially take your GraphQL server down.  provied security with these techniques:



Timeout
The first strategy and the simplest one is using a timeout to defend against large queries. This strategy is the simplest since it does not require the server to know anything about the incoming queries. All the server knows is the maximum time allowed for a query.

For example, a server configured with a 5 seconds timeout would stop the execution of any query that is taking more than 5 seconds to execute.

Timeout Pros
Simple to implement.
Most strategies will still use a timeout as a final protection.
Timeout Cons
Damage can already be done even when the timeout kicks in.
Sometimes hard to implement. Cutting connections after a certain time may result in strange behaviours.






Maximum Query Depth: By analyzing the query document’s abstract syntax tree (AST), a GraphQL server is able to reject or accept a request based on its depth.Using graphql-ruby with the max query depth setting we can validate maximum query depth.

Maximum Query Depth Pros
Since the AST of the document is analyzed statically, the query does not even execute, which adds no load on your GraphQL server.
Maximum Query Depth Cons
Depth alone is often not enough to cover all abusive queries. For example, a query requesting an enormous amount of nodes on the root will be very expensive but unlikely to be blocked by a query depth analyzer.


Query Complexity
Sometimes, the depth of a query is not enough to truly know how large or expensive a GraphQL query will be. In a lot of cases, certain fields in our schema are known to be more complex to compute than others.

Query complexity allows you to define how complex these fields are, and to restrict queries with a maximum complexity. The idea is to define how complex each field is by using a simple number. A common default is to give each field a complexity of 1. Take this query for example:

query {
  author(id: "abc") { # complexity: 1
    posts {           # complexity: 1
      title           # complexity: 1
    }
  }
}
A simple addition gives us a total of 3 for the complexity of this query. If we were to set a max complexity of 2 on our schema, this query would fail.

What if the posts field is actually much more complex than the author field? We can set a different complexity to the field. We can even set a different complexity depending on arguments! Let’s take a look at a similar query, where posts has a variable complexity depending on its arguments:

query {
  author(id: "abc") {    # complexity: 1
    posts(first: 5) {    # complexity: 5
      title              # complexity: 1
    }
  }
}
Query Complexity Pros
Covers more cases than a simple query depth.
Reject queries before executing them by statically analyzing the complexity.
Query Complexity Cons
Hard to implement perfectly.
If complexity is estimated by developers, how do we keep it up to date? How do we find the costs in the first place?
Mutations are hard to estimate. What if they have a side effect that is hard to measure, like queuing a background job?




Throttling
The solutions we’ve seen so far are great to stop abusive queries from taking your servers down. The problem with using them alone like this is that they will stop large queries, but won’t stop clients that are making a lot of medium sized queries!

In most APIs, a simple throttle is used to stop clients from requesting resources too often. GraphQL is a bit special because throttling on the number of requests does not really help us. Even a few queries might be too much if they are very large.

In fact, we have no idea what amount of requests is acceptable since they are defined by the clients. So what can we use to throttle clients?

Throttling Based on Server Time
A good estimate of how expensive a query is the server time it needs to complete. We can use this heuristic to throttle queries. With a good knowledge of your system, you can come up with a maximum server time a client can use over a certain time frame.

We also decide on how much server time is added to a client over time. This is a classic leaky bucket algorithm. Note that there are other throttling algorithms out there, but they are out of scope for this chapter. We will use a leaky bucket throttle in the next examples.

Let’s imagine our maximum server time (Bucket Size) allowed is set to 1000ms, that clients gain 100ms of server time per second (Leak Rate) and this mutation:

mutation {
  createPost(input: { title: "GraphQL Security" }) {
    post {
      title
    }
  }
}
takes on average 200ms to complete. In reality, the time may vary but we’ll assume it always takes 200ms to complete for the sake of this example.

It means that a client calling this operation more than 5 times within 1 second would be blocked until more available server time is added to the client.

After two seconds (100ms is added by second), our client could call the createPost a single time.

As you can see, throttling based on time is a great way to throttle GraphQL queries since complex queries will end up consuming more time meaning you can call them less often, and smaller queries may be called more often since they will be very fast to compute.

It can be good to express these throttling constraints to clients if your GraphQL API is public. In that case, server time is not always the easiest thing to express to clients, and clients cannot really estimate what time their queries will take without trying them first.

Remember the Max Complexity we talked about earlier? What if we throttled based on that instead?

Throttling Based on Query Complexity
Throttling based on Query Complexity is a great way to work with clients and help them respect the limits of your schema.

Let’s use the same complexity example we used in the Query Complexity section:

query {
  author(id: "abc") {    # complexity: 1
    posts {              # complexity: 1
      title              # complexity: 1
    }
  }
}
We know that this query has a cost 3 based on complexity. Just like a time throttle, we can come up with a maximum cost (Bucket Size) per time a client can use.

With a maximum cost of 9, our clients could run this query only three times, before the leak rate forbids them to query more.

The principles are the same as our time throttle, but now communicating these limits to clients is much nicer. Clients can even calculate the costs of their queries themselves without needing to estimate server time!








Pagination on Graphql:

offset based pagination
curosr based pagination (rely)



Caching in Graphql:
client side caching
server side caching 

1. application layer (resolver layer, dataloader layer)
2. using get request can cache in browser end, cdn end and cloudflare and webserver (nginx, apache etc.)

Performance:

client side caching

get request for quries

solve N + 1 problem

Demand control query with control  paginating, query depth and query complexity analysis

JSON (with GZIP)

performance monitoring with opentelemetry



Securtiy:

transport layer security: when using HTTP for queries and mutations, you should use HTTPS to encrypt data, set appropriate timeout durations for requests, and, if using HTTP caching, ensure sensitive data is cached privately (or not at all).


Demand control:

Trusted documents: 

paginated fields: A first step toward implementing demand control for a GraphQL API is limiting the amount of data that can be queried from a single field. When a field outputs a List type and the resulting list could potentially return a lot of data, it should be paginated to limit the maximum number of items that may be returned in a single request. if not limit then if anyone try to fetch 1k or 10k row a singl query then databased can be crash and if it will dos attach then database crash confirm.


Depth limiting: One of GraphQL’s strengths is that clients can write expressive operations that reflect the relationships between the data exposed in the API. However, some queries may become cyclical when the fields in the selection set are deeply nested: Even when the N+1 problem has been remediated through batched requests to underlying data sources, overly nested fields may still place excessive load on server resources and impact API performance. For this reason, it’s a good idea to limit the maximum depth of fields that a single operation can have. 


Breadth and batch limiting: 


Rete limiting:

Query Complexity analysis:

Rate limiting + query complexity: using leak bucket algorithm we can use rate limiting and query complexity .


Schema considerations:

validating and sanitizing argument values:

introspection:

Error messages:


Authentication and authorization:
