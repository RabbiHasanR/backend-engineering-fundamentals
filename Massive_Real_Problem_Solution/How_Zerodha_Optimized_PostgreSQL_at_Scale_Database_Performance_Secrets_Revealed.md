Here is a summary and an easy-to-understand breakdown of the tech talk by the Zerodha engineer.

### **The Big Picture**

Zerodha is a massive stockbroker in India handling billions of trades. This talk focuses on their back-office system called **Console**, where users check their past trades, profit/loss, and tax reports. Because the stock market is only open during the day, this system is **read-heavy during the day** (users checking reports) and **write-heavy at night** (bulk importing all the day's trades).

Instead of following traditional "best practices," Zerodha does some very unconventional—but highly effective—things with PostgreSQL to handle 50+ Terabytes of data efficiently with a very small engineering team.

---

### **Key Topics Explained the Easy Way**

#### **1. Database Design: Denormalize and Don't Over-Index**

* **The Problem:** In college, developers are taught to "normalize" data (split data into many small tables so nothing is duplicated). But when you have millions of rows, joining 5 massive tables together to get one report is incredibly slow.
* **The Zerodha Solution:** They **denormalize**. They intentionally duplicate data into wide, flat tables so they don't have to use `JOIN` queries. It takes up more disk space, but the query speed is lightning fast.
* **On Indexing:** Don't put an index on every column. Indexes take up a lot of storage space. They only index the columns that users search for directly. If a background backend job is slow because of no index, they let it be slow.

#### **2. The "No Auto-Vacuum" Rule**

* **What is Vacuuming?** In Postgres, when you delete or update a row, the old data isn't instantly removed; it becomes "dead space." Vacuuming is the process of cleaning up that dead space so the database stays fast. Usually, Postgres does this automatically (`autovacuum`).
* **The Zerodha Solution:** They **turn autovacuum off**. Because they dump millions of records into the database all at once at night, an automatic vacuum running at the same time would freeze the system. Instead, they run a manual script to clean up immediately *after* their massive night imports are finished.

#### **3. Architecture: No Replicas or Master/Slave Setup**

* **The Problem:** Most massive apps have a "Master" database (for writing) and multiple "Slave/Replica" databases (for reading) to handle the load. Managing this is complex.
* **The Zerodha Solution:** They don't use replicas at all.
* They "shard" (split) their data by financial year. Old years are put on a completely separate, cheaper database server.
* They use a feature called **Foreign Data Wrapper (FDW)**, which allows their main database to talk to the older databases seamlessly.
* If their database completely crashes, they don't have a hot backup standing by. Instead, they just restore it from Amazon S3. Because they are a back-office app, a few minutes of downtime is acceptable.



#### **4. The "Crazy" Caching Hack (The Secret Sauce)**

* **The Problem:** If millions of users ask the main 50TB database for their profit/loss reports at the same time, the database will crash.
* **The Zerodha Solution:** They built an asynchronous caching layer using a *second* Postgres database.
* When you ask for a report, the request goes to an app called SQL Jobber.
* Jobber pulls the data from the Main DB *slowly and safely*.
* It takes your specific report and saves it as a **brand new, dedicated table** in the Caching DB.
* For the rest of the day, any time you refresh your page, you are reading from that temporary table, completely leaving the Main DB alone.
* **The Crazy Part:** This process creates **20 to 30 million new tables every single day**. Every night, they wipe the disk drive completely clean (using `rm -rf`) and start fresh the next morning.



#### **5. Data Management: Delete Your Data**

* **The Problem:** Companies love hoarding data "just in case," causing their databases to bloat to hundreds of terabytes, making everything slow.
* **The Zerodha Solution:** They mercilessly delete data from their hot database. They only keep the last 15 days of hot data, plus one checkpoint backup per month. Everything else is zipped up and stored cheaply on Amazon S3. If they need to recalculate a user's entire history, they pull it from S3, calculate it, and put it back.

#### **6. Let the Database Do the Math**

* **The Problem:** Many developers pull millions of raw numbers from the database into their application code (like Python, Node, or Ruby) and write code to calculate the sum, average, or profit. This uses massive amounts of RAM and time.
* **The Zerodha Solution:** Push the math to Postgres. Postgres is written in highly optimized C. If you need the sum of a million rows, ask Postgres to do the `SUM()` inside the database and just send you the final answer.

#### **7. Postgres DB Tuning Around Queries**

* **The Problem:** Many developers apply "one-size-fits-all" settings to their entire database. They change global memory or cleanup settings, which might make one table faster but completely bottleneck another table that serves a different purpose.
* **The Zerodha Solution:** They tune the database specifically for the *queries* being run on *individual tables*.
* If one massive table runs heavy math queries, they give *only that table* more CPU parallel workers.
* They use the **Query Planner** (`EXPLAIN ANALYZE`) to see exactly how Postgres searches for data.
* They use **Partial Indexes**  to index only a specific slice of data (like `status = 'active'`) rather than the whole table. They build the database architecture to support the query, rather than hoping the query survives the database.

#### **8. Understanding the Query Planner (The Database's GPS)**

* **The Problem:** When dealing with massive data, a query might look perfectly fine in your code but take forever to run. Many developers just look at the total execution time at the bottom of an error log without understanding *how* the database actually tried to fetch the data.
* **The Zerodha Solution:** At the scale of billions of rows, understanding Postgres's "Query Planner" (using the `EXPLAIN` command) is absolutely mandatory.
* Think of the Query Planner as a GPS. You give Postgres a destination (your SQL query), and the planner calculates the route.
* The speaker notes that Postgres can be "funny"—with massive data, changing one tiny `WHERE` clause or reducing the dataset slightly can cause the planner to pick a completely different, much slower route for no obvious reason.
* **Why it matters at this scale:** If you don't understand the "direction" of the query (which table it scans first, how it sorts the data, what kind of join it chooses), you cannot fix performance issues. No amount of throwing RAM at the server or adding random indexes will save you if the database is taking a fundamentally terrible route to find your data.

### **Summary of the Speaker's Philosophy**

Don't blindly follow textbooks or what massive tech giants do. Understand your exact data flow (when is it read? when is it written?), accept that some queries are okay being slow, don't be afraid to delete useless data, and build the simplest architecture that actually solves your problem.
