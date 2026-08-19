# Partitioning — how one topic scales past one machine

> A **partition** is one append-only log file living on one broker.
> A **topic** is just a *name* over N of those partitions.

**Remember it as:** *the topic is the table, the partitions are its shards.*

A topic with 3 partitions is really 3 separate logs — `orders-0`, `orders-1`, `orders-2` — each on a (possibly) different broker, each with its own independent offset counter.

---

## Why partitions exist

Without partitioning, an entire topic lives on **one broker**. That single machine caps:

- **size** — the topic can't grow past that disk
- **throughput** — all reads and writes hit one machine's network and CPU
- **availability** — that broker dies, the whole topic is gone

Partitioning splits the topic across many brokers, so all three limits become *cluster-sized* instead of *machine-sized*. That's horizontal scaling.

---

## Who is responsible for what

| | **Topic** (logical) | **Partition** (physical) |
| --- | --- | --- |
| Storage | stores nothing itself | holds the actual bytes on disk |
| Offsets | none — "offset 5 of `orders`" is meaningless | owns its own counter `0,1,2,3…` |
| Ordering | **no** topic-wide order | strict order guaranteed inside it |
| Naming / grouping | yes — `orders`, `payments` | no |
| Retention config | set here, per topic | applies to it |
| Subscription | consumers subscribe to a topic | assigned to consumers, one at a time |
| Replication | no | **yes** — the replica unit is the partition |

Short version: the **topic is the contract, the partition is the machinery.**

---

## Where a message lands — the key decides

```text
producer sends (key="cust-42", value={...})

        hash("cust-42") % 3   ->   1
                                    |
topic: orders  (3 partitions)       v
  orders-0 [ a  d  g ]        broker-1
  orders-1 [ b  e  h ]  <-----broker-2   all cust-42 events land here, always
  orders-2 [ c  f  i ]        broker-3
```

The rule: **`partition = hash(key) % partition_count`**

Two consequences worth memorising:

- **Same key → always same partition.** This is the *only* ordering guarantee Kafka gives you.
- **No key (`key=null`) → spread across all partitions** (round-robin / sticky batching). Great for throughput, but you've given up ordering.

---

## Ordering: inside a partition only

```text
orders-0:  A1  A2  A3        <- A's events, in order. guaranteed.
orders-1:  B1  B2

merged view of the topic?  A1 B1 A2 B2 A3  or  B1 A1 A2 A3 B2  or ...
                           ^ no guarantee whatsoever
```

So the key is a **design decision, not a detail**: pick the key by *what must stay in order*.

- Need each order's lifecycle in sequence → key by `order_id`
- Need each user's actions in sequence → key by `user_id`

This is the "data locality" idea — related data must sit in the same partition to be processed together.

---

## Parallelism: partitions cap your consumers

Inside one consumer group, **a partition is read by at most one consumer**. So partitions are the hard ceiling on parallel consumption.

```text
3 partitions, 3 consumers        3 partitions, 5 consumers
  P0 -> C1                         P0 -> C1
  P1 -> C2                         P1 -> C2
  P2 -> C3                         P2 -> C3
  (perfect)                        C4, C5 -> idle, doing nothing
```

Rule of thumb: **partitions >= consumers**. Adding consumers past the partition count buys you exactly zero extra throughput. See [consumers.md](consumers.md).

---

## Does *this* service actually need ordering?

Ask one question: **would processing two events for the same entity out of order give a wrong final state?**

| Ordering **matters** | Ordering **doesn't matter** |
| --- | --- |
| Order lifecycle — `created → paid → shipped → delivered` | Metrics / telemetry — you aggregate, order is irrelevant |
| Payments & ledger — balance is a running total | Log & audit collection — each line is independent |
| Inventory — `reserve` then `release` | Email / SMS / push notifications — each is standalone |
| CDC from a database — `INSERT` then `UPDATE` on a row | Search indexing where the event carries the full document |
| State machines — any status transition | Image/file processing jobs — each job is self-contained |
| Compacted topics — last write per key wins | Click / pageview streams feeding a counter |

The pattern: **ordering matters when an event mutates state built by earlier events.** If each event is a complete, independent fact, order is free to break.

Two shortcuts that let you skip ordering:

- **Idempotent + commutative handlers** — "set status = shipped" instead of "advance status". Applying twice, or out of order, still lands correctly.
- **Version / timestamp in the payload** — the consumer drops anything older than what it already applied. Ordering becomes the consumer's problem, not Kafka's.

And note the scope: it's almost always **per-entity ordering** ("this order's events in sequence"), never global ("all orders in sequence"). Per-entity is exactly what `hash(key) % N` gives you — so you need a *good key*, not one partition. Collapsing a topic to a single partition for this caps you at one consumer forever.

---

## Choosing the partition count

| Mistake | What it costs you |
| --- | --- |
| **Too few** | Throughput ceiling; can't add consumers; one slow partition stalls a whole slice of traffic |
| **Too many** | More open files, more memory and metadata on *every* broker, slower rebalances |

### If ordering doesn't matter — start small, grow freely

Start at 3–6, watch consumer lag, add partitions when you need more consumers. Resizing is safe because nothing depends on the key mapping.

### If ordering matters — over-provision at creation

You can't grow safely later, so the two costs aren't comparable:

| | Cost |
| --- | --- |
| Over-provisioned partitions | a few MB of RAM, slightly slower rebalance |
| Under-provisioned, then resized | **ordering guarantee permanently broken** |

One is a rounding error, the other is a correctness bug. Pay the rounding error.

```text
partitions = ceil( peak_throughput / per_consumer_throughput ) x headroom
```

Measure the denominator by running **one consumer against one partition** — including its downstream work, since the DB write is usually the real bottleneck, not Kafka.

> 20k msg/sec target, one consumer sustains 2k/sec → `20000/2000 = 10` → round to **12**, take **24** for headroom.

- Size for **peak traffic 2–3 years out**, not today's.
- Pick a **highly composite number** — 12, 24, 60 — so it divides evenly across 2, 3, 4, 6, 8, 12 consumers.
- Floor of **6–12 for any ordered topic**, even at trivial traffic today. Idle partitions are nearly free; broker cost scales with *throughput*, not partition count. (The "partitions are expensive" advice is from the ZooKeeper era — KRaft handles tens of thousands per broker.)

### The resize trap

- Partitions can be **added**, never **removed**.
- Adding them **breaks the existing key mapping** — `hash(k) % 3` and `hash(k) % 4` give different answers, so old and new events for the same key sit in different partitions and ordering is silently gone for every key that moved.
- **Compacted topics can never be repartitioned at all** — the old value for a moved key is stranded in its old partition forever, so you end up with two live values for one key. See [log-compaction.md](log-compaction.md).

If you truly must grow an ordered topic: **new topic, not resize.** Create `orders.v2`, dual-write, let consumers drain `orders` to zero lag, then cut over. Safe because a key is never read from both topics at once.

---

---

## Hot partitions — the classic key mistake

A bad key concentrates traffic:

```text
key = country          key = user_id
  P0 [ BD ] ########     P0 [ ~33% ] ###
  P1 [ US ] #            P1 [ ~33% ] ###
  P2 [ UK ] #            P2 [ ~33% ] ###
   ^ one broker melts, the other two idle
```

Choose a **high-cardinality, evenly distributed** key. If your natural key is skewed, salt it (`user_id:bucket`) — but only if you don't need strict ordering on the original key.

---

## What partitions buy you — the recall list

- **Distribution** — topic data spread across brokers in the cluster
- **Scalability** — topic grows beyond one machine's disk
- **Parallelism** — N partitions = up to N consumers working at once
- **Fault tolerance** — one broker dies, partitions on other brokers stay available (with [replication.md](replication.md))
- **Ordering** — strict sequence, per partition, per key

---

## Related

- [topics.md](topics.md) — the logical log partitions sit under
- [brokers.md](brokers.md) — the machines partitions physically live on
- [replication.md](replication.md) — how a partition survives a broker dying
- [consumers.md](consumers.md) — how partitions get assigned to readers
