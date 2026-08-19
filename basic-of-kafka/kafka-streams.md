# Kafka Streams — stateful processing inside your own app

> **Kafka Streams** is a *library* you embed in your service, not a cluster you run. A Streams app
> is a consumer group that reads topics, transforms/aggregates/joins the records, and writes the
> results back to Kafka — with the machinery for **remembering things across records** already
> built in.

**Remember it as:** *a consumer group that can remember — and writes down what it remembers back
into Kafka, so it can never truly forget.*

No new servers, no scheduler, no YARN/Mesos. You deploy it exactly like any other service: a JAR,
a container, N replicas.

---

## The problem it solves

A plain consumer is fine when each record can be handled on its own: validate it, push it to an
API, write a row. The moment the answer depends on *previous* records, you are on your own:

- "how many orders has this customer placed?"
- "join every order with the customer's current profile"
- "how many failed logins per IP in the last 5 minutes?"

Now you must invent answers to hard questions: where does that running state live? What happens
when the process crashes mid-count? When a partition is reassigned to another instance, how does
the state follow it? How do you avoid double-counting after a restart?

**Kafka Streams is that machinery, pre-built.** State, its durability, and its movement during
rebalances are handled for you.

### The three ways to do stateful processing

| | Plain consumer, state in memory | Consumer + external DB (Redis/PG) | Kafka Streams |
| --- | --- | --- | --- |
| Lookup latency | ns | network hop per record | µs (local disk/memory) |
| Survives a crash | ❌ state gone | ✅ | ✅ (changelog replay) |
| State follows a rebalance | ❌ manual | ⚠️ only if keyed correctly by hand | ✅ automatic |
| Extra infrastructure | none | a second system to run | none |
| State ↔ offset consistency | you write it | **hard** — two systems, no shared transaction | ✅ one transaction |
| Throughput scaling | — | DB becomes the bottleneck | scales with instances |

**"Just use Redis" is the tempting wrong answer.** It costs a network round-trip on *every* record,
and it creates two systems that can disagree: you committed the offset but the Redis write was
lost, or vice versa. There is no transaction spanning Kafka and Redis. Streams keeps the state and
the offset in the same system, so they commit together.

---

## When to use it — and when not to

**Use it for:**

- continuous transform / filter / enrich of a stream
- aggregations: counts, sums, running totals per key
- joins: stream↔table (enrichment), stream↔stream (correlating two event flows)
- windowed analytics: per-minute, per-hour, session windows
- materialized views: a topic turned into a queryable "current state" table

**Don't use it for:**

- **batch or ad-hoc analytics** — that's Spark/Flink-batch/a warehouse. Streams is for a query you
  defined once and run forever.
- **queries that cross partitions** — each instance can only see its own share of the state. "Give
  me the global top 10" is not a natural Streams query.
- **low-volume glue work** — a plain consumer is simpler; don't pay for machinery you don't need.

**The Python reality:** Kafka Streams is JVM-only. There is no official Python port. Your options
are [ksqldb.md](ksqldb.md) (SQL over streams, same engine underneath, no JVM code from you), a
Python stream framework (Faust-style), or a plain consumer plus your own store — in which case
everything below is the design you'd have to reimplement by hand. Learning the model is worth it
either way.

---

## Core vocabulary

| Term | What it is |
| --- | --- |
| **Topology** | The DAG of processing steps: sources → operators → sinks. Defined once at startup. |
| **KStream** | A stream of *events*. Every record is an independent fact. Append-only. |
| **KTable** | A *changelog view*: latest value per key. A new record for a key **replaces** the old. |
| **GlobalKTable** | A KTable fully replicated to **every** instance — for small lookup data. |
| **Stateless operator** | `map`, `filter`, `flatMap` — no memory needed. |
| **Stateful operator** | `count`, `aggregate`, `reduce`, joins, windows — needs a state store. |
| **Task** | The unit of work and of state ownership: one task per input partition. |
| **Thread** | Runs one or more tasks. Instances have several threads. |

### The one idea that makes the rest obvious: stream ⇄ table duality

They're the same data seen two ways.

```text
stream (KStream)          →  replay it, keeping latest per key  →  table (KTable)
table (KTable)            →  emit every change as a record      →  stream (changelog)
```

A KTable *is* a compacted topic, conceptually — latest-value-per-key, deletion via `null`
(tombstone). That's not a coincidence; it's literally how Streams stores it. See
[log-compaction.md](log-compaction.md).

---

## The scaling model: one task per partition

```text
input topic: 4 partitions

  P0  P1  P2  P3
  │   │   │   │
  T0  T1  T2  T3        4 tasks (fixed by partition count)
  └───┬───┘   └──┬──┘
  instance A   instance B
```

- Tasks are created from the **partition count** — a task is never split.
- Adding instances **moves tasks**, it doesn't create more of them.
- **Max parallelism = number of partitions.** A 4-partition topic can never use more than 4
  instances usefully. See [partitioning.md](partitioning.md).
- The rebalance protocol is the ordinary consumer-group one — see [consumers.md](consumers.md).

Crucially: **a task owns the state for its partitions' keys, and nothing else.**

---

## Local state store

A **state store** is an embedded key-value store living *inside the application process* — RocksDB
on local disk by default, or in-memory if you ask for it. Not a server. Not a network service. A
directory on the same machine as the task.

**Why local:**

- lookups are microseconds — no network hop on the hot path
- throughput scales linearly with instances, because each instance has its own store
- the state is right next to the code that uses it, so operations like "read the running count,
  add one, write it back" are cheap enough to do per record

**The partitioning contract.** A task holds state only for the keys in *its* partitions. That works
only because a key's records always land in the same partition (see
[partitioning.md](partitioning.md)) — so exactly one task ever owns a given key. That is why the
key matters so much, and it leads directly to:

### Repartition topics

If your topology changes the key (a `groupBy` on a different field, for example), the old
partitioning no longer matches the new key. Records for the same *new* key could be sitting in
different partitions, owned by different tasks — the ownership contract breaks.

So Streams silently writes the re-keyed records to an **internal repartition topic**
(`<app-id>-<name>-repartition`), partitioned by the new key, and reads them back. Correctness is
restored, at the cost of a full round-trip through the broker. This is the main hidden cost in a
topology — re-key once, not repeatedly.

**And then the obvious problem:** local disk dies with the machine. Which is what the changelog is
for.

---

## Changelog topic

Every write to a state store is *also* produced to an internal Kafka topic named
`<app-id>-<store-name>-changelog`, keyed by the store key.

**It is a compacted topic** ([log-compaction.md](log-compaction.md)) — and it has to be. Time-based
retention would eventually delete the only copy of a key that hasn't changed recently, leaving you
unable to rebuild full state. Compaction gives the exact property needed: **bounded disk, complete
state.** Deleting a key from the store produces a **tombstone** (`null` value).

### The restore path

```text
instance A dies
   ↓
group rebalances, task T2 is assigned to instance B
   ↓
B creates an empty local store, replays the T2 changelog partition from offset 0
   ↓
local store is identical to what A had → processing resumes
```

The state is durable and replicated **because Kafka replicated it** — the changelog is an ordinary
topic with an ordinary replication factor ([replication.md](replication.md)). You get no new
storage system to back up or monitor.

### Standby replicas

Replaying a large changelog takes time, and the partition is not being processed while it does.
`num.standby.replicas=1` tells other instances to keep a warm copy of the store continuously
up-to-date from the changelog. On failure, a standby takes over in seconds rather than minutes.

The cost: extra disk and extra network on every instance. Worth it whenever recovery time matters
more than hardware.

### Practical traps

- **Restore time grows with store size.** A multi-GB store is a multi-minute outage for those
  partitions. Standbys, or a smaller state footprint, are the fixes.
- **Never produce to a changelog topic by hand**, and never delete it while the app is running —
  Streams owns it and assumes it is the exact mirror of local state.
- **The `application.id` is part of the state's identity.** Internal topics are named after it.
  Changing it orphans all existing state and starts from nothing. Deliberately resetting an app
  means deleting its internal topics (there's a reset tool for this) — otherwise the old state
  quietly comes back.
- Internal topics count against cluster quotas and partition budgets — a big topology can create a
  surprising number of them.

---

## How the three fit together

```text
                    input topic (partitioned by key)
                              │
                              ▼
                 ┌────────────────────────┐
                 │   task (one partition) │
                 └────────────────────────┘
                    read ↕ write  (µs)
                 ┌────────────────────────┐
                 │  LOCAL STATE STORE     │   ← speed
                 │  (RocksDB, this host)  │
                 └────────────────────────┘
                              │ every write mirrored
                              ▼
                 ┌────────────────────────┐
                 │  CHANGELOG TOPIC       │   ← durability
                 │  (compacted, replicated)│
                 └────────────────────────┘
                              │
              on crash/rebalance: replay into a new local store
                              ▼
                    task resumes on another instance
```

### Worked example: running order count per customer

1. `order` for `customer42` arrives on partition 3; task T3 owns it.
2. T3 reads `customer42` from its **local store** → `17`. Microseconds, no network.
3. Increments to `18`, writes it back to the local store.
4. Streams also produces `(customer42 → 18)` to the **changelog topic**, partition 3.
5. The offset commit, the store write, and the changelog write commit **together**.
6. The instance crashes.
7. Rebalance moves T3 to another instance, which replays changelog partition 3 into a fresh local
   store. **Compaction** means that replay is one record per customer, not every increment ever.
8. `customer42` reads back as `18`. Processing continues. Nothing was lost, nothing double-counted.

### The division of labour

| Piece | Job |
| --- | --- |
| **Partitioning** | decides *who owns which keys* — makes single-owner state possible |
| **Local state store** | **speed** — per-record read/modify/write without a network hop |
| **Changelog topic** | **durability + mobility** — state survives crashes and follows rebalances |
| **Log compaction** | **bounded size** — the changelog stays replayable without growing forever |
| **Replication** | the changelog itself survives broker loss |

Remove any one and the design collapses: no local store → slow; no changelog → state dies with the
host; no compaction → the changelog grows forever and restores take hours; no partitioning
contract → two instances fight over the same key.

---

## Exactly-once, briefly

Per record, Streams does three writes: the local store, the changelog, and the consumed offset. If
those aren't atomic, a crash between them means the count is replayed and **double-counted**.

`processing.guarantee=exactly_once_v2` wraps output records, changelog writes, and offset commits
in a single Kafka transaction. Either all land or none do. This is what makes "my aggregate is
correct after a crash" true rather than aspirational.

The cost is latency: results become visible only at transaction commit (`commit.interval.ms`, a
few hundred ms). The default guarantee is at-least-once — fine for idempotent work, wrong for
counters and sums.

---

## Windowing and joins, briefly

- **Windowed stores** are state stores whose keys include a time window, with their own retention —
  old windows are dropped, so the store stays bounded.
- **Grace period**: how long a window still accepts late-arriving records before it's closed and
  cleaned. Late data after that is dropped — this is a business decision, not a default to accept
  blindly.
- **KStream–KTable join** is the everyday enrichment pattern: an event stream joined against a
  table of current reference data (orders × customer profiles). The table side is a local state
  store, so the join is a local lookup.
- **GlobalKTable** avoids the repartitioning a normal join requires, since every instance has the
  whole table — only viable for small, slow-changing lookup data.

---

## When you need this

- **"Restart takes forever before it processes anything"** → changelog replay of a large store. Add
  `num.standby.replicas`, or shrink the state.
- **"My state disappeared"** → `application.id` changed, or internal topics were deleted. State
  identity is tied to the app id.
- **"Counts are wrong / doubled after a crash"** → running at-least-once. Set
  `processing.guarantee=exactly_once_v2`.
- **"Strange topics appeared in my cluster"** → they're yours: `*-changelog` (state durability) and
  `*-repartition` (re-keying). Don't touch them manually.
- **"One instance is hot, the rest idle"** → key skew; state and load both follow the key. See
  [partitioning.md](partitioning.md).
- **"I added instances and nothing got faster"** → parallelism is capped by the input partition
  count.
- **"A groupBy made everything slow"** → it inserted a repartition topic; every record now does a
  round-trip through the broker.
- **"I need a global aggregate"** → each instance only sees its own keys. Write results to a topic
  and aggregate that downstream, or rethink the key.

---

## Related

- [consumers.md](consumers.md) — the consumer-group and rebalance model Streams is built on
- [partitioning.md](partitioning.md) — why one key belongs to exactly one task
- [log-compaction.md](log-compaction.md) — what makes a changelog replayable and bounded
- [replication.md](replication.md) — why the changelog is durable without new infrastructure
- [topics.md](topics.md) — retention modes, including the compacted internals used here
- [ksqldb.md](ksqldb.md) — the same engine, driven by SQL instead of code
- [kafka-connect.md](kafka-connect.md) — getting data in and out at the edges of a topology
