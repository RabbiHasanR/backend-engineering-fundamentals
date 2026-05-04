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
