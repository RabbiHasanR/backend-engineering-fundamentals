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

This list is **only for the first handshake**. The client connects to whichever one answers, asks for metadata, learns the full cluster layout, and then connects directly to the leaders it needs.

Two consequences:

* You do **not** need to list every broker — 2–3 is enough. Any broker can answer "who leads what".
* You list more than one **for redundancy only**, so startup still works if one is down.

---

## Leader and follower are *per partition*, not per broker

The most common misunderstanding. Look at the diagram again: broker 1 is the leader of P0 **and** a follower of P2 — at the same time.

There is no "master broker" handling all traffic. Leadership is spread across partitions so every broker does real work.

(One broker does additionally act as the **controller**, which assigns partitions and elects leaders — but that's a background admin role, not a traffic role.)

---

## When a broker dies

1. Its partitions lose their leader.
2. For each one, a **follower on another broker is promoted** to leader.
3. Clients refresh metadata, discover the new leader, and reconnect.

No data lost, no downtime — as long as replication factor > 1. Details in [replication.md](replication.md).

Brokers can also **join or leave without downtime**; partitions get rebalanced across the new set.

---

## Quick recall

| Question | Answer |
| --- | --- |
| What is a broker? | One machine running Kafka; a node in the cluster |
| What does it store? | Some partitions of some topics — never a whole topic |
| Who does the producer send to? | Directly to the **leader** of that partition |
| How does it find the leader? | Asks any broker for metadata (that's `bootstrap.servers`) |
| Is a broker a leader or a follower? | Both — leadership is **per partition** |
| What if it dies? | A follower is promoted; clients reconnect |
| Why so simple? | No per-message logic = high throughput |

**Next:** [partitioning.md](partitioning.md) → how topics are split across brokers · [replication.md](replication.md) → how copies survive failure · [topics.md](topics.md) → what's being stored
