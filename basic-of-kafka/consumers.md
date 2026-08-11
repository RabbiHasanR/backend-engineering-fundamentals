# Consumers & Consumer Groups — who reads the log

> A **consumer** is one running process that reads events from a topic.
> A **consumer group** is a label that says which processes are on the same team.

**Remember it as:** *consumers do the work, the group decides how the work is split.*

---

## Three words people mix up

| Term | What it actually is |
| --- | --- |
| **Consumer** | One running process — e.g. one Docker container running your Python worker |
| **Server** | The machine hosting that container. **Kafka does not care about it at all** |
| **Consumer group** | Just a string — `group.id` — set in your client config |

Kafka identifies teams by that string and nothing else. Not hostname, not IP, not PID. Same `group.id` = same team, even across different data centres. Different `group.id` = unrelated services, even in the same container.

---

## The golden rule

> **One partition is read by at most one consumer within the same group.**

Memorize this one. Every behaviour below falls out of it.

---

## `group.id` in code — you must set it yourself

Kafka never generates one for you:

```python
from confluent_kafka import Consumer

consumer = Consumer({
    "bootstrap.servers": "broker1:9092,broker2:9092",
    "group.id": "email-workers",        # required — omit it and this fails
    "auto.offset.reset": "latest",
})
consumer.subscribe(["ticket_purchased_events"])
```

**Why it can't be automatic:** `group.id` is an identity that has to survive restarts. A random one per boot would find no committed offset in `__consumer_offsets`, fall back to `auto.offset.reset`, and replay or skip everything on *every* deploy.

**Rule:** one `group.id` per **service**, from config or an env var — never per instance. All 4 replicas of the email worker share `email-workers`. That's what makes them a team instead of 4 services doing the same job 4 times.

> Watch out: some frameworks (Spring Kafka) invent a random `group.id` when you don't set one. That's the broken behaviour above, silently. Always set it.

---

## Scaling out — one group, more instances

Topic `ticket_purchased_events`, **4 partitions**, `group.id="ticket-workers"`:

```text
1 consumer   →  P0 P1 P2 P3  all on one process
2 consumers  →  P0 P1 | P2 P3          (Kafka rebalances automatically)
4 consumers  →  P0 | P1 | P2 | P3      (maximum parallelism)
5 consumers  →  P0 | P1 | P2 | P3 | (idle)
```

Three things to take away:

- **Rebalancing is automatic.** Add or kill pods freely; Kafka reassigns partitions across whoever is alive.
- **Partition count is the hard ceiling.** 4 partitions means 4 workers maximum doing useful work. To go faster you must add partitions — see [partitioning.md](partitioning.md).
- **The idle 5th isn't wasted.** It's a hot standby. When one of the four dies, it picks up that partition within seconds.

---

## Fan-out — different groups, same topic

The checkout service publishes **one** event to `ticket_purchased_events`. Three unrelated services need it:

```text
                                    ┌──► email-workers      (PDF ticket → user, must be fast)
   ticket_purchased_events ─────────┼──► inventory-workers  (mark seat sold in PostgreSQL)
                                    └──► fraud-ai-workers   (AI inference, deliberately slow)
```

Different `group.id` → Kafka treats them as completely independent readers, each getting **every** message.

| Property | What it buys you |
| --- | --- |
| **Zero interference** | Fraud service crawling at offset 4500 doesn't hold back email at offset 5000 |
| **Fault isolation** | Inventory dies on a DB lock → email keeps running; on restart inventory resumes exactly where it stopped |
| **Extensibility** | Add `loyalty-workers` six months later and it reads the whole history — **zero changes to existing services** |

**The mechanism behind all three:** the read position is stored **per group** in `__consumer_offsets` — three independent bookmarks over one shared log. See [topics.md](topics.md) for offsets, lag, and `auto.offset.reset`.

---

## Queue or pub/sub — your choice

| You want | Do this |
| --- | --- |
| **Queue** — each message handled once by the team | Put all consumers in **one** group |
| **Pub/Sub** — everyone gets everything | Give each consumer its **own** group |

Same topic, same broker, no config change on the Kafka side. The `group.id` string alone decides which pattern you get.

---

## When you need this

- **One process can't keep up** (lag climbing) → add instances to the same group, up to the partition count.
- **New feature must react to existing events** → new `group.id`. Don't touch the producing service, don't touch the other consumers.
- **Ordering matters** → order is only guaranteed *within* a partition, so key by entity (`seat_id`) to keep one seat's events on one partition and in order.
- **Gotcha:** adding consumers past the partition count changes nothing. Raise partitions first.

---

## Related

- [topics.md](topics.md) — offsets, `__consumer_offsets`, lag, where a new group starts
- [partitioning.md](partitioning.md) — why partition count caps your parallelism
- [events.md](events.md) — what a consumer actually receives
