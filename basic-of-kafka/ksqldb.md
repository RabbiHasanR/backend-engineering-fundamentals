# ksqlDB — stream processing you declare in SQL instead of writing in code

> **ksqlDB** is an event-streaming database for Kafka. You submit SQL; it compiles that SQL into a
> [Kafka Streams](kafka-streams.md) topology and runs it forever on its own cluster of servers,


> next to the brokers. The results land back in Kafka topics, and can also be queried directly.

**Remember it as:** *Kafka Streams with the Java taken out and a SQL prompt put in its place.*

It is not a plugin inside the brokers, and it is not a library inside your app. It is a third

thing: a separate, horizontally scalable, fault-tolerant cluster whose entire job is running
continuous queries.

---

## The problem it solves

Say you need "block any IP with 5+ failed logins in a minute." With [Kafka
Streams](kafka-streams.md) that is a **new JVM service**: a Java project, a build, a container, a
deployment, replicas, monitoring, an on-call story — for what is, conceptually, one `GROUP BY`.

That is a bad trade when your stack is Python/Django or Go. You do not want a Java service in the
estate just to aggregate a topic, and you cannot use Kafka Streams from Python at all — it is
JVM-only.

ksqlDB moves that work **from application code into infrastructure**. You stand up the ksqlDB
cluster once, then every new piece of stream logic is a SQL statement submitted over REST, not a
new service to build and own. State, windowing, restarts and crash recovery are the cluster's
problem, not yours.

**The honest cost:** you are trading N application deployments for one more cluster to operate.
Below a certain amount of stream logic, that trade is not worth it — a plain consumer is simpler
than either option.

---

## Where it sits

```text
   ksql CLI        your Django/FastAPI app        Java client
       │                    │ REST                     │
       └────────────┬───────┴──────────────────────────┘
                    ▼
        ┌───────────────────────────────────┐
        │   ksqlDB cluster                  │   servers sharing one ksql.service.id
        │   ┌────────┐ ┌────────┐ ┌────────┐│   each runs Kafka Streams internally
        │   │server 1│ │server 2│ │server 3││   each has a local RocksDB state store
        │   └────────┘ └────────┘ └────────┘│   embedded Kafka Connect (optional)
        └───────────────────────────────────┘
                    │ ordinary consumer + producer traffic
                    ▼
        ┌───────────────────────────────────┐
        │   Kafka brokers                   │
        └───────────────────────────────────┘
```

The servers are **external client processes** — they never run on the brokers. To Kafka they look
like any other producer/consumer group. Everything ksqlDB "remembers" is stored in Kafka topics,
which is why any server can pick up any other server's work after a crash.

**Four ways in:**

| Interface | Use it for |
| --- | --- |
| **ksql CLI** | interactive exploration, ad-hoc `SELECT`, defining streams by hand |
| **REST API** | how your application integrates — submit statements, run queries, read results |
| **Java client** | typed access to push/pull queries from JVM code |
| **Embedded Kafka Connect** | declaring source/sink connectors in SQL, no separate Connect cluster |

For a Python backend, **the REST API is the interface that matters.** Everything else is
convenience.

---

## Streams vs Tables

ksqlDB sees a Kafka topic through one of two lenses. Picking the wrong one is the most common
beginner mistake, because both are the same topic underneath.

| | **STREAM** | **TABLE** |
| --- | --- | --- |
| A record means | "this happened" — a fact | "this key's value is now X" |
| A repeated key | two independent events | the second **replaces** the first |
| Shape | append-only history | latest value per key |
| Example | `login_attempts`, `orders`, `clicks` | `user_profile`, `current_inventory` |
| `null` value | just a record with no value | **tombstone** — delete this key |

This is the same **stream ⇄ table duality** as in [kafka-streams.md](kafka-streams.md):

```text
STREAM  → replay it, keep the latest value per key →  TABLE
TABLE   → emit every change as a record            →  STREAM (its changelog)
```

A TABLE is conceptually a compacted topic — latest-value-per-key, deletes via tombstone. That is
not an analogy; it is literally how ksqlDB stores materialized tables. See
[log-compaction.md](log-compaction.md).

**The rule of thumb:** if a later record about the same key *corrects or replaces* an earlier one,
you want a TABLE. If both records are independently true, you want a STREAM.

---

## The SQL surface: two very different kinds of statement

The draft version of this note showed one `CREATE TABLE … AS SELECT` and moved on. That statement
does far more than it looks like, so the distinction is worth being precise about.

### 1. `CREATE STREAM` / `CREATE TABLE` — registering an existing topic

This creates **no data and runs no query**. It is a schema declaration: "topic `X` exists, here is
how to read it."

```sql
CREATE STREAM failed_logins (
    ip_address VARCHAR KEY,
    user_id    VARCHAR,
    attempt_at BIGINT
) WITH (
    KAFKA_TOPIC  = 'failed_logins',
    VALUE_FORMAT = 'AVRO',
    TIMESTAMP    = 'attempt_at'
);
```

- **`VALUE_FORMAT`** — `JSON`, `AVRO`, `PROTOBUF`, `JSON_SR`, `DELIMITED`. With Avro/Protobuf,
  ksqlDB pulls the schema from the registry instead of you typing the columns; see
  [schema-registry.md](schema-registry.md).
- **`KEY`** decides partitioning, and therefore who can aggregate or join on it — see
  [partitioning.md](partitioning.md).
- **`TIMESTAMP`** picks *event time* over ingestion time. This matters enormously the moment you
  window: without it, a record delayed by the network is counted in the wrong minute.

### 2. `CREATE … AS SELECT` (CSAS / CTAS) — starting a persistent query

This is the one that does real work.

```sql
CREATE TABLE blocked_ips AS
    SELECT ip_address, COUNT(*) AS failure_count
    FROM failed_logins
    WINDOW TUMBLING (SIZE 1 MINUTE)
    GROUP BY ip_address
    HAVING COUNT(*) >= 5;
```

That single statement:

1. compiles to a Kafka Streams topology,
2. **runs forever** as a *persistent query* — it survives your CLI disconnecting, and survives
   server restarts,
3. creates a **real new Kafka topic** (`BLOCKED_IPS`) that any consumer in any language can read,
4. maintains a **materialized state store** so the current counts can be queried directly,
5. and quietly creates the internal changelog/repartition topics needed to make that durable.

**A persistent query is a deployment.** `DROP TABLE blocked_ips;` stops it and, with
`DELETE TOPIC`, removes its output. Treat these statements with the seriousness of a migration,
not of a `SELECT`.

---

## Push vs pull queries

Two ways to get results out, and they answer different questions.

| | **Push query** (`EMIT CHANGES`) | **Pull query** |
| --- | --- | --- |
| Question | "tell me every time this changes" | "what is the value **right now**?" |
| Connection | long-lived stream (HTTP chunked) | ordinary request/response |
| Ends | never, until you disconnect | immediately |
| Reads from | the running topology | the materialized state store |
| Works on | streams and tables | **materialized tables only** |

```sql
-- push: a live feed, keeps emitting
SELECT * FROM blocked_ips EMIT CHANGES;

-- pull: one answer, then done
SELECT failure_count FROM blocked_ips WHERE ip_address = '10.0.0.7';
```

**The trap:** a pull query only works against a table that ksqlDB actually **materialized** — one
created by a `CREATE TABLE … AS SELECT` with an aggregation. A table you merely registered over an
existing topic has no state store behind it, and the pull query fails. "Why does my pull query say
the table isn't materialized" almost always means the table was declared, not derived.

**The second trap:** the state is partitioned across servers, so a pull query for a key owned by
another server has to be forwarded to it. ksqlDB does this for you, but it means pull queries are
*not* a general-purpose database read path — they are a keyed lookup, nothing more.

---

## What is actually underneath

This is the part that explains every ksqlDB failure mode: **a persistent query is a Kafka Streams
application.** ksqlDB inherits the whole model from [kafka-streams.md](kafka-streams.md) — you just
didn't write it.

- **One task per input partition.** Parallelism is capped by the partition count. Adding a 5th
  server to a 4-partition topic does nothing.
- **Local RocksDB state stores** on each server — µs lookups, no network hop per record.
- **Changelog topics** (`_confluent-ksql-<service-id>…-changelog`, compacted) mirror every state
  write, so a server that dies can have its state rebuilt elsewhere by replay.
- **Repartition topics** appear whenever a `GROUP BY` or join re-keys the data. Every record then
  makes an extra round-trip through the brokers — the main hidden cost of a query.
- **The servers form a consumer group.** Adding or losing one triggers an ordinary rebalance; see
  [consumers.md](consumers.md).
- **`ksql.service.id` is the cluster's identity.** All servers in one cluster share it, and the
  internal topic names are derived from it. Changing it orphans all existing state — exactly like
  changing `application.id` in a Streams app.

Scaling is therefore: **add servers with the same `ksql.service.id`**, up to the partition count of
your input topics. There is no other knob.

---

## Windows and joins, briefly

**Windows** bound an aggregation in time, so state stays finite:

| Window | Shape | Typical use |
| --- | --- | --- |
| `TUMBLING (SIZE 1 MINUTE)` | fixed, non-overlapping | "per-minute counts" |
| `HOPPING (SIZE 5 MINUTES, ADVANCE BY 1 MINUTE)` | fixed, overlapping | rolling 5-min average |
| `SESSION (30 SECONDS)` | gap-defined, variable length | user activity bursts |

`GRACE PERIOD` is how long a closed window still accepts late-arriving records. Records later than
that are **dropped silently**. This is a business decision — how late is too late — and the default
is not the right answer for everyone.

**Joins** are the everyday enrichment pattern:

- **stream ↔ table** — enrich each event with current reference data (orders × customer profile).
  A local state-store lookup, cheap.
- **stream ↔ stream** — correlate two event flows, requires a `WITHIN` time bound because neither
  side is finite.
- **table ↔ table** — keep a joined materialized view up to date.

**Co-partitioning is required.** Both sides must be keyed on the join column and have the **same
partition count**, or records that should meet end up on different servers. A join that silently
returns nothing is nearly always this.

---

## Correctness under crashes

ksqlDB sets `processing.guarantee` on the Streams apps it runs. With `exactly_once_v2`, the output
records, the state-store changelog writes and the consumer offset commit all land in **one Kafka
transaction** — see
[Exactly-Once-Semantics-Transactions.md](Exactly-Once-Semantics-Transactions.md).

Without it you get at-least-once, which is fine for idempotent transforms and **wrong for counters
and sums**: a crash mid-window replays records and inflates the aggregate. If your query has a
`COUNT` or `SUM` in it, this setting is not optional.

The price is latency — results become visible only at commit, on the order of a few hundred ms.

---

## Getting data in and out

ksqlDB can embed [Kafka Connect](kafka-connect.md), so the edges are SQL too:

```sql
CREATE SOURCE CONNECTOR pg_orders WITH (
    'connector.class' = 'io.debezium.connector.postgresql.PostgresConnector',
    'database.hostname' = 'pg',
    'table.include.list' = 'public.orders'
);
```

Source connectors act as producers, sink connectors as consumers. Embedded mode is genuinely handy
for development and small setups; for anything serious, run a **dedicated Connect cluster** so that
connector load and query load cannot starve each other.

---

## Choosing between the three options

| | Plain consumer | Kafka Streams | ksqlDB |
| --- | --- | --- | --- |
| Written in | any language | Java/Scala only | SQL |
| Deployment unit | your service | your service | a SQL statement |
| Extra infrastructure | none | none | **a ksqlDB cluster** |
| State handling | you build it | built in | built in |
| Who operates it | app team | app team | platform team |
| Ceiling | low — no state machinery | very high — arbitrary code | medium — SQL's limits |
| Fits a Python stack | ✅ | ❌ | ✅ (via REST) |

The progression is real: start with a plain consumer, reach for ksqlDB when the logic becomes
stateful and the team isn't JVM, and drop to Kafka Streams when SQL runs out of road.

---

## When *not* to use it

- **It is not an OLAP database and not a Postgres replacement.** Pull queries are keyed lookups
  against a state store. No ad-hoc scans, no arbitrary secondary-index queries, no reporting.
- **No global or cross-partition queries.** Each server sees only its own keys. "Global top 10" is
  not a natural query — emit results to a topic and aggregate downstream.
- **Complex logic outgrows SQL.** Once you're bending SQL around control flow, calling external
  APIs, or writing user-defined functions in Java anyway, the SQL layer has stopped paying for
  itself. Write a Streams app.
- **Interactive mode is a shared mutable cluster.** Anyone with CLI access can start a persistent
  query — a deployment — with no review. The production answer is **headless mode**: the cluster
  boots from a SQL file kept in version control, and the interactive endpoint is disabled. Your
  stream logic then goes through pull requests like everything else.
- **Licensing.** ksqlDB is under the **Confluent Community License**, not Apache 2.0 — usable, but
  it forbids offering it as a competing managed service. If vendor neutrality matters,
  **Flink SQL** is the Apache-licensed alternative solving the same problem.

---

## Worked example, end to end

Goal: block IPs with 5+ failed logins per minute, consumed by a Django app.

**1. A topic already exists**, produced by the auth service:

```text
failed_logins   6 partitions, keyed by ip_address
```

**2. Register it** (declaration only, nothing runs yet):

```sql
CREATE STREAM failed_logins (
    ip_address VARCHAR KEY, user_id VARCHAR, attempt_at BIGINT
) WITH (KAFKA_TOPIC='failed_logins', VALUE_FORMAT='AVRO', TIMESTAMP='attempt_at');
```

**3. Derive the table** — this starts a persistent query:

```sql
CREATE TABLE blocked_ips WITH (KAFKA_TOPIC='blocked_ips', PARTITIONS=6) AS
    SELECT ip_address, COUNT(*) AS failure_count
    FROM failed_logins
    WINDOW TUMBLING (SIZE 1 MINUTE, GRACE PERIOD 10 SECONDS)
    GROUP BY ip_address
    HAVING COUNT(*) >= 5
    EMIT CHANGES;
```

**4. What now exists in the cluster:**

```text
failed_logins                    ← input, yours
BLOCKED_IPS                      ← output, a real topic anyone can consume
_confluent-ksql-…-changelog      ← compacted, backs the windowed state store
                                   (no repartition topic — already keyed by ip_address)
```

No repartition topic appears because the stream was **already keyed** by `ip_address`. Grouping by
`user_id` instead would have added one, plus a full broker round-trip per record.

**5. Two ways for Django to use it:**

```sql
-- pull: "is this IP blocked right now?" — synchronous, in the request path
SELECT failure_count FROM blocked_ips WHERE ip_address = '10.0.0.7';
```

…or just **consume the `BLOCKED_IPS` topic** with `confluent-kafka-python` and write bans into
Postgres or Redis. This second option is usually the better one: the output is an ordinary topic,
so ksqlDB stops being a runtime dependency of your request path.

**6. A server dies.** Its partitions are reassigned, the new owner replays the changelog into a
fresh local store, and counting resumes. Compaction means that replay is one record per IP, not
every increment ever — see [log-compaction.md](log-compaction.md).

---

## When you need this

- **"Pull query says the table isn't materialized"** → the table was *declared* over a topic, not
  *derived* with `CREATE TABLE … AS SELECT`. Only derived, aggregated tables have a state store.
- **"A query sits in REBUILDING / RESTORING forever"** → replaying a large changelog after a
  rebalance. Same fix as Streams: standby replicas, or less state.
- **"I added servers and nothing got faster"** → parallelism is capped by the input topic's
  partition count.
- **"My join returns nothing"** → co-partitioning. Both sides must be keyed on the join column with
  the **same partition count**.
- **"Unknown `_confluent-ksql-*` topics appeared"** → they're yours: changelogs and repartition
  topics. Never produce to them or delete them while queries run.
- **"Counts are inflated after a restart"** → running at-least-once. Set `exactly_once_v2`.
- **"Results are missing for records that arrived late"** → the window closed; they fell outside the
  grace period. Check that `TIMESTAMP` points at event time, not ingestion time.
- **"My queries vanished after a config change"** → `ksql.service.id` changed, so the cluster is
  looking at a different set of internal topics. It's the state's identity.
- **"Someone dropped a table in production"** → interactive mode. Move to headless mode with the
  SQL in version control.

---

## Related

- [kafka-streams.md](kafka-streams.md) — the engine ksqlDB compiles to; read it to understand why
  ksqlDB behaves the way it does
- [partitioning.md](partitioning.md) — keys, co-partitioning, and why parallelism has a ceiling
- [consumers.md](consumers.md) — the consumer-group and rebalance model the servers use
- [log-compaction.md](log-compaction.md) — what makes tables and changelogs replayable and bounded
- [topics.md](topics.md) — the underlying storage every stream and table is built on
- [schema-registry.md](schema-registry.md) — where Avro/Protobuf column definitions come from
- [kafka-connect.md](kafka-connect.md) — getting data into and out of Kafka at the edges
- [Exactly-Once-Semantics-Transactions.md](Exactly-Once-Semantics-Transactions.md) — why aggregates
  survive a crash intact
