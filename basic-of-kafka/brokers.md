# Brokers — the machines that hold the log

> A **broker** is one computer, VM, or container running the Kafka process.
> Many brokers together = a **Kafka cluster**.

**Remember it as:** *a broker is just a server that owns some partitions and serves them.*

That's it. It is **intentionally very simple** — it does not route, filter, transform, or track per-message state. It appends bytes to disk and hands bytes back. Same idea as *the broker is a dumb pipe on purpose* in [events.md](events.md): dumb broker = fast broker.

---

## What a broker is responsible for

| Job | Why it matters |
| --- | --- |
| **Stores partition data on disk** | Append-only writes → sequential I/O → very fast |
| **Serves produce (write) requests** | Producers write here |
| **Serves fetch (read) requests** | Consumers read here |
| **Is leader for some partitions, follower for others** | Leader handles the traffic; followers copy it |
| **Replicates from the leaders it follows** | This is what survives a machine dying |
| **Serves cluster metadata** | Tells clients "partition 1 lives on broker 2" |

A broker does **not** store a whole topic. It stores *some partitions* of *some topics* — see [partitioning.md](partitioning.md).

---

## Example — a 3-broker cluster

Topic `orders`, 3 partitions, replication factor 2:

```text
        Broker 1          Broker 2          Broker 3
        --------          --------          --------
        P0 (leader)       P1 (leader)       P2 (leader)
        P2 (follower)     P0 (follower)     P1 (follower)
```

Every broker leads one partition and backs up another. Load is spread evenly — no single machine is the bottleneck, and no single machine's death loses data.

### Trace one message end to end

```text
1. producer connects to ANY broker  → "who leads orders-P1?"
2. broker replies                   → "broker 2"
3. producer sends the message DIRECTLY to broker 2   (the leader)
4. broker 2 appends it to P1 on disk
5. broker 3 (follower of P1) fetches it and copies it
6. consumer fetches from broker 2   (the leader)
```

**The point to remember:** after step 2 the producer talks **straight to the leader**. There is no proxy, no middleman broker forwarding traffic. That's why Kafka scales — more partitions on more brokers means more independent leaders handling traffic in parallel.

---

## Bootstrap servers — why it's a *list*

```text
bootstrap.servers = broker1:9092,broker2:9092,broker3:9092
```

**It is the seed list your client uses for its very first connection, only to discover the rest of the cluster.** Every client does this — producers, consumers, and admin clients alike. What actually happens on startup:

```text
1. client picks one address from the list, connects
2. client sends a Metadata request:  "describe the cluster"
3. broker replies with the FULL picture:
      - every broker in the cluster (id, host, port)
      - every partition, and which broker leads it
4. client drops the bootstrap list and connects
   DIRECTLY to the leaders it needs
```

Hence the name — it exists to get you started, like a bootloader.

Three consequences:

* **It is not a proxy or gateway.** The broker you bootstrap against is usually *not* the one you end up sending data to. No traffic is forwarded through it.
* **You don't need to list every broker.** 2–3 is standard even in a 50-broker cluster — any broker knows the full layout.
* **You list several purely for startup redundancy.** List only one and it's down when your app boots, the client can't start — even if the other 49 brokers are healthy. In Kubernetes or a managed service this is often a single DNS name that resolves to any healthy broker.

### Two things people get wrong

**There is no "bootstrap server" component.** Those entries are ordinary brokers. In the cluster above, broker 1 can be a bootstrap address *and* leader of P0 *and* follower of P2 — all at once. The word is a **role in a moment**, not a type of machine.

**It's the first connection, not the only one.** Metadata is refreshed periodically (`metadata.max.age.ms`, default 5 min) and immediately on errors like `NotLeaderOrFollowerException` after a failover. But those refreshes go to a broker the client is *already* connected to — the bootstrap list only comes back into play if the client loses every connection and has to start over.

**Remember it as:** *`bootstrap.servers` is a phone book entry, not a phone line.* Look up the number once, then call directly.

> Debugging note: the client connects when metadata is first needed, so a wrong `bootstrap.servers` usually shows up as a timeout on your first `send()` — not as an error when the producer is created.

---

## Leader and follower are *per partition*, not per broker

The most common misunderstanding. Look at the diagram again: broker 1 is the leader of P0 **and** a follower of P2 — at the same time.

There is no "master broker" handling all traffic. Leadership is spread across partitions so every broker does real work.

(One broker does additionally act as the **controller**, which assigns partitions and elects leaders — but that's a background admin role, not a traffic role.)

---

## When a broker dies — worked through

Say **broker 2 dies** in the cluster above. Two *different* things happen at once, and separating them is the whole lesson:

| Partition | What it lost | What happens |
| --- | --- | --- |
| **P1** | its **leader** | Broker 3 (follower) is **promoted to leader**. Automatic, seconds. |
| **P0** | its **follower** | **Nothing.** Broker 1 is still leader and serves reads/writes as normal. |
| **P2** | nothing | Unaffected — leader and follower both alive. |

Clients find out by refreshing metadata — the same mechanism as bootstrap, just repeated. That's why failover is invisible to application code.

### But P0 gets no new follower

Broker 3 does **not** pick it up. P0 is now **under-replicated** — 1 copy instead of 2. It keeps working, but has no backup: if broker 1 also dies, that data is gone.

**Why doesn't Kafka just move the replica to broker 3?** Because **replica assignment is static** — decided at topic creation, never rebalanced on failure. A dead broker usually means a restart, a deploy, or a brief network blip. Auto-copying replicas on every blip would shift terabytes across the network, then shift it all back when the broker returns. **Kafka assumes brokers come back.**

How P0 actually recovers:

* **Normal case** — broker 2 restarts → rejoins → fetches from broker 1 to catch up → rejoins the ISR. Back to 2 copies, no human involved.
* **Broker 2 is gone for good** — *you* move it manually with `kafka-reassign-partitions.sh` ("P0's replicas are now brokers 1 and 3"). Tools like Cruise Control automate this, but it is not core Kafka.

### The part that bites in production

While P0 is under-replicated, if the producer uses `acks=all` and the topic has `min.insync.replicas=2`, **writes to P0 start failing** with `NotEnoughReplicasException`.

Not because data was lost — broker 1 is fine — but because Kafka refuses a write it cannot durably back up. It fails loudly instead of silently accepting data with no redundancy.

**Remember it as:** *under-replicated doesn't mean broken, it means one more failure away from broken.* That's why `UnderReplicatedPartitions` is the metric everyone alerts on. More in [replication.md](replication.md).

Brokers can also **join or leave without downtime** — but note this means *serving* traffic resumes automatically; moving existing partition data to a new broker is still a deliberate reassignment.

---

## Quick recall

| Question | Answer |
| --- | --- |
| What is a broker? | One machine running Kafka; a node in the cluster |
| What does it store? | Some partitions of some topics — never a whole topic |
| Who does the producer send to? | Directly to the **leader** of that partition |
| How does it find the leader? | Asks any broker for metadata (that's `bootstrap.servers`) |
| Is `bootstrap.servers` a proxy? | No — first handshake only, then clients talk straight to leaders |
| Are bootstrap servers special machines? | No — ordinary brokers. It's a role, not a type |
| Is it used again after startup? | Only if the client loses every connection; refreshes use already-connected brokers |
| Is a broker a leader or a follower? | Both — leadership is **per partition** |
| A broker dies and a partition loses its **leader**? | A follower is promoted; clients reconnect |
| A broker dies and a partition loses its **follower**? | Nothing moves — it just runs under-replicated |
| Does Kafka rebuild the missing replica elsewhere? | No. Assignment is static; restart the broker or reassign manually |
| Cost of under-replication? | With `acks=all` + `min.insync.replicas=2`, writes fail |
| Why so simple? | No per-message logic = high throughput |

**Next:** [partitioning.md](partitioning.md) → how topics are split across brokers · [replication.md](replication.md) → how copies survive failure · [topics.md](topics.md) → what's being stored
