# KRaft & the Controller — who decides who leads what

> The **controller** is the one broker allowed to make cluster-wide decisions — mainly *which
> replica leads each partition*.
> **KRaft** is Kafka storing that decision-making state in an internal Kafka topic instead of
> in ZooKeeper.

**Remember it as:** *the controller decides **leadership**; KRaft decides **where that decision
is stored**.*

---

## The metadata somebody has to hold

Running a cluster means constantly tracking:

- **partition state** — online / offline
- **leader replica and in-sync replicas (ISR)** per partition
- **topic configurations**
- **partition locations** — which broker holds what

This is small data but *hot* data: every producer and consumer needs the current answer, and it
changes every time a broker dies, restarts, or a topic is created.

---

## What the controller actually does

| Job | Why it needs a single decider |
| --- | --- |
| Elect the **leader** of each partition | Only the leader accepts writes |
| Track the **ISR** | Decides who is eligible to be promoted |
| React to a broker **joining or dying** | Reassign every partition the dead broker led |
| Own topic/partition **creation and config** | One authoritative view of what exists |

**Why exactly one?** Two active controllers = split-brain: both promote a different replica of
the same partition, both start accepting writes, and the two logs diverge with no way to merge
them. Brokers never negotiate leadership among themselves — they serve data and *obey*.

---

## The ZooKeeper era — and its three walls

Metadata must survive the controller dying, so early Kafka kept it in **ZooKeeper**, a separate
consensus system. Correct, but it hit three structural limits:

| Failure | What went wrong | Consequence |
| --- | --- | --- |
| **Broker failure** | Every partition on the dead broker needs a leader election, and each result is a **separate un-batched write** to ZooKeeper | Recovery cost scales with partition count — infeasible past **~200k partitions** |
| **Controller failure** | The new controller holds metadata in memory, so it must **load the entire state from ZooKeeper** before it can act | Cold start, minutes on a big cluster |
| **Diverging views** | The controller *pushes* updates to brokers. If it dies after notifying brokers 1–3 but not 4–6… | Brokers silently disagree about who leads what, and nothing detects it |

Plus the operational tax: two distributed systems to deploy, tune, secure and upgrade — and you
could never lean on new ZooKeeper features, because every user would have to upgrade their
ZooKeeper cluster first.

---

## KRaft's insight

> Metadata is just an **ordered log of changes** — and Kafka is already the best log there is.
> So let Kafka store its own metadata.

- Metadata lives in the internal topic **`__cluster_metadata`**, a **single partition**.
- **Controller nodes** replicate it among themselves using **Raft** (hence *K-Raft*).
- The **Raft leader *is* the active controller.**
- Controller nodes can be colocated with brokers, or run as their own processes.

### Problem → fix

| ZooKeeper pain | KRaft fix |
| --- | --- |
| Un-batched write per partition on failover | Leadership changes are **appended as batched log records** |
| Cold controller start | Standby controllers **already tail the log** → state is warm, failover is sub-second |
| Diverging broker views | Brokers **pull the same ordered log** and track their offset — "broker 4 is at offset 900, leader at 1000" is *measurable lag*, not invisible inconsistency |
| Two systems to run | One binary, one protocol, one security model — much easier to deploy in the cloud |

---

## Design decisions worth knowing

**Every entry is fsynced to disk, not buffered in memory.** Slower per write, but the metadata
log is the thing you can least afford to lose.

**Quorum instead of ISR.** ISR replication commits only when the *slowest* in-sync replica acks.
Fine for data topics — bad here, because this one partition gates the entire cluster. Raft
commits at a **majority** (3 of 5), so one slow controller can't stall metadata.
*Trade-off:* you tolerate ⌊n/2⌋ failures instead of n−1 — acceptable because the quorum is small
and dedicated, and you can afford to devote more nodes to it.

**Pull-based, not push-based.** Followers fetch from the leader:

- more **batching** in message sending
- a node that is **no longer a voter** learns it on its next fetch — the leader tells it directly
- so it won't sit there timing out and starting **disruptive elections**, the way a stale
  push-based node does

---

## Keeping the log from growing forever

The metadata log only ever grows, so it's compacted by **snapshots**:

```text
[ snapshot @ offset 5000 ] + [ 5001 5002 5003 … ]  =  current state
        ↑                            ↑
   whole state at that point     only the tail is replayed
```

Recovery = load the snapshot, then apply the log entries after it.

---

## Combined vs dedicated mode

A single process can hold **both** roles — it runs Raft consensus for `__cluster_metadata` *and*
serves normal produce/fetch traffic. Even then it needs a **separate controller listener**, which
is the clue that these stay two distinct roles sharing one process.

| | Combined (`broker,controller`) | Dedicated |
| --- | --- | --- |
| **Use for** | local dev, CI, small test clusters | production |
| **Shape** | 1 node, quorum of one | 3 controllers + N brokers |

Why production separates them:

- **Resource contention** — a heavy consumer backfill saturating disk also slows a Raft voter,
  and every broker depends on that voter to learn about leadership changes.
- **Merged failure domains** — rolling-restart a broker and you also removed a controller vote.
  With 3 combined nodes you're one unplanned failure from losing quorum during routine work.
- **Opposite scaling curves** — the quorum wants to stay small and odd (3 or 5; Raft gets
  *slower* with more voters), brokers want to grow with data volume.

**Roles are fixed when the storage directory is formatted** — you can't flip a node between
combined and dedicated in place. Switching means re-provisioning, so pick dedicated up front for
anything that might become real.

---

## When you need this

- **Quorum size** — keep it **odd and small** (3, or 5). More voters is not more throughput.
- **Combined mode in production** — couples every broker restart to quorum health. Don't.
- **ZooKeeper is gone** — deprecated in Kafka **3.5**, removed in **4.0**. KRaft isn't an
  alternative anymore, it's the only mode.
- **"Controller failover is slow"** — a ZooKeeper-era problem. In KRaft the standby is already
  caught up; if failover is slow now, look elsewhere.
- **Huge partition counts** — the old ~200k ceiling was a ZooKeeper write-rate limit, not a Kafka
  one. KRaft clusters go far past it.

---

## Related

- [brokers.md](brokers.md) — the nodes the controller is managing
- [replication.md](replication.md) — ISR, leaders and followers on the data path
- [partitioning.md](partitioning.md) — why partition *count* is what stressed ZooKeeper
- [topics.md](topics.md) — the log structure KRaft reuses for its own metadata
