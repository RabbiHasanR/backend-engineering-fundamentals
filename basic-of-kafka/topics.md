# Topics — the named log you write events into

> A **topic** is a named, append-only log of events.
> Producers append to the end. Consumers read forward from wherever they want.

**Remember it as:** *a Postgres table you can only `INSERT` into — never `UPDATE`, never `DELETE` — and every reader keeps their own bookmark.*

That's the whole idea. Everything else (partitions, replicas, brokers) is just *how* Kafka makes that log big, fast, and hard to lose.

---

## What a topic is responsible for

| Job | Why it matters |
| --- | --- |
| **Naming / grouping related events** | `orders`, `payments`, `user.signups` — one stream per kind of thing |
| **Durable ordered storage** | Written to disk, append-only, survives restarts |
| **Retention** | Decides how long the events stay readable |
| **Decoupling** | Producers never know who consumes; consumers never know who produced |
| **Being the unit you subscribe to** | Consumers say "read topic `orders`", nothing finer |

### What a topic is **not** responsible for

- **It does not delete on read.** Reading is not consuming-away. Ten consumers can read the same event.
- **It does not track who read what.** That's the consumer group — see [consumers.md](consumers.md).
- **It does not physically store anything itself.** A topic is a logical name; the bytes live in *partitions* on *brokers* — see [partitioning.md](partitioning.md) and [brokers.md](brokers.md).

---

## Example — the `orders` topic

```text
topic: orders

offset:     0        1        2        3        4      <- next write goes here (5)
          +--------+--------+--------+--------+--------+
          | ord-A  | ord-B  | ord-C  | ord-D  | ord-E  |
          +--------+--------+--------+--------+--------+
               ^                          ^
               |                          |
        billing-service            email-service
        (reading at 1)             (reading at 4)
```

Two independent services, **same events**, different positions. Neither blocks the other, and neither removes anything.

`ord-C` is written once and never changes. If the order is cancelled, you don't edit offset 2 — you **append a new event** (`ord-C-cancelled`) at offset 5. The log is the history; correcting the past means adding to the present. Same immutability rule as [events.md](events.md).

---

## Offsets — the position of an event in the log

An **offset** is just a sequence number — `0, 1, 2, 3…` — assigned by the broker when the event is appended. Never reused, never reassigned, never changed.

Because it's immutable and always increasing, the offset is effectively the event's **permanent address**.

### Offsets are per *partition*, not per topic

This is the part people get wrong. Every partition has its own independent counter:

```text
orders-P0:  0  1  2  3  4  5
orders-P1:  0  1  2  3  4  5
                        ^--- offset 5 in P0 and offset 5 in P1
                             are two completely different messages
```

So "offset 5 of the topic `orders`" is meaningless. A real address is always **(topic, partition, offset)** → `orders-P1-5`.

### Who stores which offset

| Stored by | What it is |
| --- | --- |
| **Broker** | The offset baked into the log itself — the event's address |
| **Consumer group** | Its *own* current position, the **committed offset**, saved in the internal `__consumer_offsets` topic |

That split is the reason two consumers can read the same topic independently, and the reason a crashed consumer resumes where it left off instead of restarting from zero.

### Lag — the number you actually monitor

```text
          committed offset (2)        log-end offset (5)
                  |                          |
          +---+---+---+---+---+
          | 0 | 1 | 2 | 3 | 4 |
          +---+---+---+---+---+
                    <----------->
                      lag = 3
```

**lag = log-end offset − committed offset** = how many events behind the consumer is.
Lag growing steadily = your consumer is slower than your producer. This is the Kafka metric to put on a Grafana dashboard.

### Where a brand-new consumer starts

Set with `auto.offset.reset`, and it only applies when there's **no committed offset yet**:

- `earliest` → start at offset 0, replay the entire retained history
- `latest` → start at the end, only see events produced from now on

Note that offsets don't live forever — retention deletes the oldest segments, so offset 0 eventually stops existing.

---

## Reading is seek-by-offset only

A topic is **not** an indexed database. There is no `WHERE order_id = 42`.

You can only:

- start from the beginning,
- start from the end,
- jump to a specific offset (or a timestamp, which Kafka maps to an offset),

then read **forward, sequentially**.

That limitation *is* the performance. Sequential disk reads and writes are what make Kafka fast — see [brokers.md](brokers.md). If you need lookups, push the data into Postgres/Elasticsearch with [kafka-connect.md](kafka-connect.md) and query it there.

---

## Retention — how long events stay

Configured **per topic**. Three flavours:

| Mode | Config | Use it when |
| --- | --- | --- |
| **Time** | `retention.ms` (default 7 days) | The normal case — "keep a week of orders" |
| **Size** | `retention.bytes` | Disk is the hard limit — "keep 50 GB, drop the rest" |
| **Compacted** | `cleanup.policy=compact` | You want the **latest value per key**, forever |

Compaction is the interesting one: instead of deleting by age, Kafka keeps the most recent event for each key and throws away older versions of that same key. The topic becomes a rebuildable snapshot of current state — perfect for things like "current price per product".

```text
before compaction:  (user1, A) (user2, X) (user1, B) (user1, C) (user2, Y)
after  compaction:  (user1, C) (user2, Y)
```

---

## Topic vs queue

| | Traditional queue | Kafka topic |
| --- | --- | --- |
| After a read | Message is removed | Message stays until retention expires |
| Multiple consumers | They split the messages | Each group gets the **full** stream |
| Replay | Gone forever | Reset the offset and read it again |

That replay ability is the single biggest practical difference — see [Message-Queue-Architecture-Guide.md](Message-Queue-Architecture-Guide.md).

---

## Designing topics — practical rules

- **One event type per topic.** `orders.created` and `orders.shipped` are different topics, not a `type` field you filter on.
- **Name them `noun.verb`, past tense** — `payments.settled`, `users.registered`. Events are facts that already happened.
- **Don't over-split.** Every topic costs partitions, file handles, and metadata on every broker. A topic per customer is a classic mistake.
- **Don't under-split either.** A single `events` topic that everything dumps into forces every consumer to read and discard 90% of the traffic.
- **Set retention deliberately.** The 7-day default is a decision you're making whether you think about it or not.

---

## Related

- [events.md](events.md) — what's actually inside a topic
- [partitioning.md](partitioning.md) — how one topic scales past one machine
- [brokers.md](brokers.md) — where the partitions physically live
- [consumers.md](consumers.md) — who tracks the offsets
