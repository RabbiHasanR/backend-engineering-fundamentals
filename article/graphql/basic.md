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