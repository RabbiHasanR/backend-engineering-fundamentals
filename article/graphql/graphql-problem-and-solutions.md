# GraphQL Problems That Will Take Down Your Production Server (and How I Fixed Them)

When and why do we choose GraphQL over REST? There are several valid reasons that fit different projects and requirements, but the headline feature is simple: the client gets the power. The client decides the shape of the response, can ask for complex deeply-nested data, and gets exactly the fields it needs. We reach for GraphQL to solve over-fetching, under-fetching, endpoint sprawl, oversized payloads, and the latency that comes with all of them.

But great power comes with great responsibility. The same flexibility that makes GraphQL elegant for clients also makes it dangerous on the server. A careless query or a malicious one can exhaust your CPU, saturate your connection pool, and bring your database to its knees. After building and shipping GraphQL services in production, I have seen these problems show up over and over. Here is what they look like, what they actually break, and how I fixed them.

---

## 1. Unbounded list queries

Look at this innocent-looking query:

```graphql
query list_of_posts {
  posts {
    id
    title
  }
}
```

If your `users` table has 1k rows, this returns 1k rows. If it has 1M rows, it returns 1M rows. The schema does not stop the client from asking for everything.

**What it causes in production:** the database has to read every row. The server holds all of them in memory to build the JSON. The response gets huge, bandwidth cost goes up, and the user stares at a frozen screen.

**How I fixed it:** I pick the pagination style based on the resource. In my project, `posts` and `comments` use Relay-style cursor pagination with the `first`, `after`, `last`, and `before` arguments and an encoded cursor, because they grow fast and need stable ordering. `users` uses simple offset-based pagination (`page`, `pageSize`), because the list is small and admins want to jump to specific pages. In both cases I enforce a fixed max page size on the server — the client cannot ask for more than the limit. The query below shows the Relay cursor pagination shape used for `posts`:

```graphql
query list_of_posts {
  posts(first: 5) {
    totalCount
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    edges {
      cursor
      node {
        id
        title
      }
    }
  }
}
```

The rule is simple: no list field is unbounded. Ever.

---

## 2. The N+1 problem

Now look at this query:

```graphql
query list_of_users {
  users(page: 1, pageSize: 10) {
    items {
      id
      email
      posts {
        id
        title
      }
    }
    pageInfo { page totalPages totalItems hasNext }
  }
}
```

Execution looks innocent: fetch 10 users from the `users` table. Then, for *each* user, the `posts` resolver runs another query against the `posts` table. That is 1 + 10 = 11 queries for a single request. Scale that to a `pageSize` of 100 and you are issuing 101 queries per request.

**What it causes in production:** database CPU jumps, the connection pool runs out, other requests start waiting in line, and the whole service slows down. This is the most common reason a GraphQL service falls over.

**How I fixed it:** DataLoader. It collects all the `posts` lookups for that request and runs them as one batched query. My stack is Python + FastAPI + Strawberry, and Strawberry has built-in DataLoader support. After adding it, the same query runs in only 2 database calls — one for users, one for all their posts — no matter how many users you ask for.

---

## 3. Depth (cyclic nesting)

You have paginated, you have batched. You feel safe. Then this query lands:

```graphql
query list_of_users {
  users(page: 1, pageSize: 5) {
    items {
      id
      posts(first: 5) {
        edges {
          node {
            author {                         # back to User
              posts(first: 5) {
                edges {
                  node {
                    author {                 # back to User again
                      posts(first: 5) {
                        edges {
                          node {
                            author { id email }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

Because `User` and `Post` reference each other, a client can cycle through them as deep as they want. Pagination does not help — every level is paginated. DataLoader does not help — every level still expands.

**What it causes in production:** the resolver tree blows up, the event loop gets stuck, response time crosses your timeout, and one request can block a worker for seconds. A few of these at the same time can take the service down.

**How I fixed it:** a depth-limit rule that checks the query before it runs. If the depth is too high, the request is rejected with a clear error. No resolvers run, no database call happens.

---

## 4. Breadth (alias abuse)

Depth is not the only axis. A client can also go wide:

```graphql
query users {
  a: users(page: 1,  pageSize: 100) { items { id email displayName } }
  b: users(page: 2,  pageSize: 100) { items { id email displayName } }
  c: users(page: 3,  pageSize: 100) { items { id email displayName } }
  d: users(page: 4,  pageSize: 100) { items { id email displayName } }
  e: users(page: 5,  pageSize: 100) { items { id email displayName } }
  f: users(page: 6,  pageSize: 100) { items { id email displayName } }
  g: users(page: 7,  pageSize: 100) { items { id email displayName } }
  h: users(page: 8,  pageSize: 100) { items { id email displayName } }
  i: users(page: 9,  pageSize: 100) { items { id email displayName } }
  j: users(page: 10, pageSize: 100) { items { id email displayName } }
}
```

Aliases let the client call the same field ten times in a single operation. From the outside it is one HTTP request — to your rate limiter, one hit. To your database, ten paginated scans.

**What it causes in production:** your rate limiter becomes useless because it counts requests, not the work behind them. One attacker with one token can do the work of hundreds of users per second. CPU and DB load go up, but your traffic graphs look flat.

**How I fixed it:** query cost analysis. Each field gets a cost, list fields multiply by their `pageSize`, aliases add up, and any query above the budget is rejected before it runs. It also gives me one clean knob to tune per-client limits later.

---

## 5. Batched N+1 (compound fan-out)

This is the boss fight. Pagination, DataLoader, depth limit, breadth limit — all in place. Then this shows up:

```graphql
query users {
  users(page: 1, pageSize: 20) {
    items {
      id
      posts(first: 10) {            # batched via posts_by_author loader
        edges {
          node {
            id
            title
            author { id email }     # batched via user_by_id loader
            comments(first: 10) {   # batched via comments_by_post loader
              edges {
                node {
                  id
                  body
                  author { id email }   # batched via user_by_id loader
                }
              }
            }
          }
        }
      }
    }
  }
}
```

Every level is batched. Every loader works correctly. The query count stays tiny. But the *row count* is `20 × 10 × 10 = 2,000` comment nodes, plus their authors, plus the post authors. DataLoader saves you on round-trips; it does not save you when the fan-out itself is the problem.

**What it causes in production:** memory usage spikes while building the JSON, GC pauses get longer, the response gets huge, and the client struggles to parse it. The database is fine — the app server is the one that falls over.

**How I fixed it:** treat depth, breadth, and complexity as one shared budget. The same cost analyzer from problem #4 multiplies costs across nested list fields, so a 20 × 10 × 10 shape becomes a real number and gets rejected if it crosses the limit. Pagination caps the leaves, depth caps the height, complexity catches the cross-product the other two miss.

---

## Conclusion

GraphQL gives the client a lot of power, and that power can hurt your server if you don't set limits. Always assume the client may send a bad or careless query. Pagination, DataLoader, depth limit, breadth limit, and query cost analysis are not extra features — they are the basics every production GraphQL server needs.

If you want to see all of this working in real code, I built a blog API server called **Tonic** using FastAPI, Python, and Strawberry GraphQL, and I fixed every problem above in that project. You can check it out here: [https://github.com/RabbiHasanR/tonic](https://github.com/RabbiHasanR/tonic)
