This talk describes a clever "software abuse" hack used by **Zerodha** (one of India's largest stockbrokers) to handle millions of complex financial reports daily. Instead of fighting the limitations of traditional databases, they pushed **PostgreSQL** to its absolute limits by creating millions of tables to store temporary data.

Here is the breakdown of the problem, the solution, and the "abuse" that makes it work.

---

## 1. The Problem: "The Report Crisis"

Zerodha has hundreds of billions of rows of data. When millions of users want to download their tax or trade reports at the same time:

* **Queries are slow:** Joining massive tables can take 30+ seconds.
* **Resource Clogging:** If 2 million people click "Get Report" simultaneously, the database crashes because it's trying to hold 2 million open connections.
* **The Inevitable Slowness:** No matter how fast your database is (Postgres, ClickHouse, etc.), scanning trillions of rows for complex logic will always be slow.

---

## 2. The Solution: "DungBeetle" Middleware

To solve this, they built a lightweight system in **Go** called **DungBeetle**. It acts as a middleman between the User App and the Big Databases.

### How it works (The Workflow):

1. **Request:** A user clicks "Get Report." The App sends a request to DungBeetle.
2. **Immediate Response:** DungBeetle says, "Got it! Here is a Job ID. I'll let you know when it's done." (This is **Asynchronous**).
3. **Traffic Control:** DungBeetle puts the request in a queue. It only sends queries to the big database at a speed the database can handle.
4. **Result Caching:** Once the big database finishes the query, DungBeetle grabs the result and writes it into a **separate, temporary "Results DB"**.
5. **Final Retrieval:** The user's App sees the job is "Done" and pulls the data instantly from the Results DB.

---

## 3. The "Abuse": 7 Million Tables

The "hack" that makes this unique is how they use the **Results DB** (which is also a PostgreSQL instance):

* **One Table Per Report:** Every single time a user requests a report, DungBeetle creates a **brand-new, unique table** just for that specific result.
* **The Scale:** On an average day, this single Postgres instance holds over **7 million tables**.
* **Metadata Heavy:** The "metadata" (the list of column names and table info) alone takes up about **60 GB** of space.
* **The Reset:** To keep it from exploding, they don't use `DROP TABLE` (which is slow). Every night, they simply **unplug the hard drive**, wipe it, and attach a fresh one.

---

## 4. Why this is "Easy" and Effective

* **Decoupling:** The main application doesn't need to know how the database works. It just asks DungBeetle for a report.
* **Language Agnostic:** Since it's a simple HTTP API, an app written in Python, Node.js, or Java can use it without needing complex database drivers.
* **Postgres is a Beast:** The speaker highlights that Postgres is so well-built that it can handle 7 million tables and still restart in only **3 seconds**.
* **User Experience:** Even if a report takes 20 seconds to generate, the user's UI doesn't "freeze." They see a "Processing..." bar and get their data the moment that dedicated table is ready.

---

## Summary Table

| Feature | Traditional Way | The DungBeetle Way |
| --- | --- | --- |
| **Connection** | Direct (Synchronous) | Queued (Asynchronous) |
| **Wait Time** | Browser hangs until done | Browser polls for "Done" status |
| **Load** | Can crash the DB during peak | Controlled, steady flow of queries |
| **Storage** | Results sent to memory/app | Results saved to a unique Postgres table |

