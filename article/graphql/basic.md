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
boject types: any object like User/Post

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
