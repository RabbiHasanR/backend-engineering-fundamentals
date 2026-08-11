# Replication — how a partition survives a broker dying

> **Replication factor (RF)** = how many copies of each partition exist, on different brokers.
> One copy is the **leader**, the rest are **followers**.

**Remember it as:** *partitioning splits the topic, replication copies each split.*

The unit of replication is the **partition**, not the topic. `RF=3` on a 3-partition topic means 9 partition copies spread over the cluster.

---

## Leader and followers

- Every partition has exactly **one leader** at a time.
- All **produces and consumes go to the leader**. Followers serve nobody.
- Followers just **fetch from the leader** continuously, copying its log byte for byte.
- They exist for one reason: to be ready to *become* leader.

This is why the old note said "an invisible process to most developers" — you never address a replica. You address a topic, the client looks up the current leader, done.

```text
topic: orders, 3 partitions, RF=3

            broker-1        broker-2        broker-3
orders-0    L               F               F
orders-1    F               L               F
orders-2    F               F               L
```

Leadership is spread on purpose — every broker leads something, so write load stays balanced instead of piling on one machine.

---

## ISR — the in-sync replica set

A follower is **in the ISR** while it keeps up with the leader (within `replica.lag.time.max.ms`, default 30s). Fall behind — slow disk, network, GC pause — and it's **kicked out of the ISR**.

Why it matters: **only an ISR member can be elected leader.** An out-of-sync replica is missing data, so promoting it would silently lose messages.

```text
before                              after broker-2 dies
orders-1: leader=broker-2           orders-1: leader=broker-3
          ISR = {2, 1, 3}                     ISR = {3, 1}

producers/consumers reconnect to broker-3 and continue
```

Failover is automatic. Clients get a "not leader for partition" error, refresh metadata, and retry against the new leader — usually invisible to your code.

---

## The producer knob — `acks`

This is the "tunable in the producer" part, and it's the only replication setting you touch day to day.

| `acks` | producer waits for | risk |
| --- | --- | --- |
| `0` | nothing — fire and forget | fastest, silent data loss |
| `1` | leader wrote it | leader dies before followers copy → **that write is gone** |
| `all` | every **ISR** member wrote it | slowest, no loss |

The pairing rule — these three only work together:

```text
RF = 3                    3 copies exist
acks = all                producer waits for the whole ISR
min.insync.replicas = 2   ISR must have >= 2 members, or the write is refused
```

`min.insync.replicas` alone does **nothing** — it's only enforced when `acks=all`. And `acks=all` without it is weak: if the ISR has shrunk to just the leader, "all" means "the leader", which is `acks=1` wearing a disguise.

---

## Worked example — payments topic

`RF=3`, `acks=all`, `min.insync.replicas=2`

| state | what happens |
| --- | --- |
| all 3 brokers up | writes accepted, ISR = 3 |
| 1 broker dies | ISR = 2, still >= min → **writes keep flowing**, no loss |
| 2 brokers die | ISR = 1, below min → producer gets **`NotEnoughReplicasException`** |

That last row is the whole point: Kafka **refuses the write instead of losing it**. You chose durability over availability. Flip `min.insync.replicas` to 1 and you get the opposite trade — it keeps accepting writes, and you accept the risk of losing them.

---

## Two things replication does *not* do

| myth | reality |
| --- | --- |
| "replicas spread read load" | followers serve **no** reads. Fetch-from-follower exists but is opt-in and only for rack locality (saving cross-AZ network cost), not throughput |
| "replication increases throughput" | it **costs** throughput — `RF=3` is 3x disk and 3x internal network, and `acks=all` adds latency |

What replication actually buys: **durability and availability**, paid for in cost and latency. Throughput and parallelism come from [partitioning.md](partitioning.md) — different tool, different problem.

---

## Choosing RF

| RF | when |
| --- | --- |
| 1 | local dev only. one broker dies = data gone |
| 2 | rarely useful — lose one broker and you can't hold `min.insync=2` |
| **3** | **the standard.** survives one broker down while staying fully durable |
| 4+ | only for cross-rack / cross-AZ critical data |

RF can never exceed the broker count. RF=3 needs at least 3 brokers.

---

## The recall list

- **Leader** — one per partition, handles all reads and writes
- **Followers** — silent copies, fetch from the leader, exist to take over
- **ISR** — replicas currently caught up; only these can be elected leader
- **`acks=all` + `min.insync.replicas=2` + `RF=3`** — the durable default
- **Trade** — durability and availability, bought with disk, network and latency

---

## Related

- [partitioning.md](partitioning.md) — the unit that gets replicated
- [brokers.md](brokers.md) — the machines replicas live on
- [topics.md](topics.md) — where RF is configured
- [consumers.md](consumers.md) — who reconnects when a leader moves
