1. Too much focus on buzzwords  
Microservices, Kafka, Redis, System Design… all good.  
But when I go little deeper into basics (collections, threads, DB transactions), answers become shaky.  
Strong foundation still matters a lot.

2. Not able to explain their own project properly  
When I ask “Can you explain your current system architecture?”  
Many give very high-level answers.  
If you worked on something daily, you should be able to draw and explain it clearly.

3. No discussion about trade-offs  
At senior level, I expect thinking like:  
Why this approach? Why not something else?  
What are the pros/cons?  
There is no perfect design. Only better decisions for a given situation.

4. Random debugging approach  
If production issue comes, how will you approach?  
Some candidates jump directly to guessing.  
I look more for structured thinking than instant solution.

5. Communication at senior level  
After 8+ years, it’s not just coding.  
It’s ownership, clarity, mentoring ability and confidence in decision making.




what is gil, treads vs asyncio vs process.. what is concurrency and when to use each.

what is db transactions? why is this important in db

when should logic live in a function or trigger instead of the app? When is that a mistake?

 how do you add a NOT NULL column to a 50M-row table without downtime?


when do you use cache and why and which approch how do you decied..and how cache invalidate or expire and how evictiion for eviction use lru or lfu.  when two requests update the same row at the same moment then what happen?






exisint working project:

What happens to a request from client → DB → response? Where is each piece of state stored?
Real numbers: RPS, DB size, p95 latency. If they worked on it every day, they should know roughly.
"What breaks if X goes down?"
"Tell me about a decision you made. What alternative did you reject, and why?"
"If you rebuilt it today, what would you change?"



Design live match scores?

desing notification service?

desing face verification service?

"Now 10× the traffic on match day"
"Mobile users are on a slow 3G connection, and some go offline"
"Redis just died"
"The mobile team needs a breaking API change, but old app versions are still in use"




when web app page load then it takes 4s now what do you do? (db index, partions,sharding)

After yesterday's deploy, p95 on /matches went from 200ms to 3s. There are no errors. Walk me through what you do."





how do you manage legesy codebase and how do you handle team and how do you handle repository where multiple member works in multple module  and continueously update code and push and continuesly need to deploy this code live. how do you manage this




ai:

how do you use ai tools in your day to day task..which things do  you do with ai tools and which not use ai and why.

how do you check ai genereated code and how do you confident this code shipt to production.

how do you manage security? in ai usages and in application? which security things do you handle mustly and why