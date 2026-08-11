# Why and When to Use Kafka

> For the *mechanics* of fan-out, batching and competing consumers across Redis / SQS / RabbitMQ / Kafka, see [Message-Queue-Architecture-Guide.md](Message-Queue-Architecture-Guide.md). This file is about the decision *before* that: should you reach for Kafka at all?

---

## 1. What Kafka Actually Is

Kafka is usually introduced as "a message queue". That framing is wrong and it causes most of the confusion later.

**Kafka is a distributed, replicated, append-only commit log.** Messages are appended to the end of a partition and written to disk. They are never removed on consumption — they expire only when the retention policy says so.

The difference from a traditional broker:

* **RabbitMQ / SQS:** the broker owns the message. A consumer acks it, the broker deletes it. The message is gone. The broker tracks per-message state.
* **Kafka:** the log owns the message. A consumer group tracks its own **offset** — a pointer into the log. Reading does not consume. Ten different consumer groups read the same bytes ten times, independently, at their own pace.

Almost every Kafka feature falls out of this one design choice:

| Because the log is retained… | You get |
| --- | --- |
| The data is still there after reading | **Replay** — reprocess history, rebuild state, recover from a bug |
| Consumers only hold an integer offset | **Cheap fan-out** — new consumer groups cost nothing on the broker |
| Writes are sequential appends | **Throughput** — sequential disk I/O, no per-message bookkeeping |
| The log is the ordering | **Per-key ordering** within a partition (see [partitioning.md](partitioning.md)) |
| The log is durable and replicated | It can be the **system of record**, not just transport (see [replication.md](replication.md)) |

---

## 2. Why Kafka Over Other Brokers

| Need | Kafka | Traditional broker (RabbitMQ / SQS / Redis) |
| --- | --- | --- |
| **Replay history** — new consumer reads from the beginning | Yes, log is retained; just reset the offset | No, the message is deleted after ack |
| **Many independent consumers of the same data** | Consumer groups, each with its own offset | Fanout exchange + N queues, N copies stored |
| **Per-key ordering at high throughput** | Ordered within a partition, parallel across partitions | SQS FIFO / single queue only — order costs throughput |
| **Throughput** | Very high (sequential appends, zero-copy, batching — see §3) | Lower — per-message state and acks |
| **Horizontal scaling** | Add partitions → add consumers in the group; add brokers → rebalance partitions across them. Scaling is a first-class, built-in concept | Scaling = add more workers on one queue, or shard queues manually. The broker itself is often the ceiling |
| **Consumer scaling limit** | One partition per consumer in a group — parallelism is bounded by partition count, so it is planned up front | Unbounded competing consumers, but no ordering guarantee |
| **Stream processing on the data** | Built in — Kafka Streams, ksqlDB | Needs an external system |
| **Source of truth / event sourcing** | The log *is* the store | Not designed for it |
| **Retention** | Time- or size-based, configurable per topic; can be infinite | Until acked |

**The one-line version:** choose Kafka when the *stream of events itself* has value beyond delivering it once — because you want to replay it, process it, or let many systems read it independently.

---

## 3. Why Kafka Is Fast

The throughput claim above isn't magic and it isn't clever code. It's four design choices that stack, and each one is really "do less work per message".

**1. Sequential append, not random writes**

A partition is an append-only file on disk ([partitioning.md](partitioning.md)). Every write goes to the end. Nothing is updated in place, so there's no B-tree to rebalance, no index to keep sorted, no free-space map, and no per-message record of "has this been delivered yet".

A traditional broker has to do the opposite: it tracks per-message delivery and ack state, deletes messages out of the middle when they're acked, and that turns into random I/O plus bookkeeping. Kafka's broker deletes nothing until a whole segment file expires by retention.

Why this matters physically: on spinning disks sequential I/O is orders of magnitude faster than random I/O because you're not paying a seek per operation. On SSDs the gap is smaller but still real — sequential writes are friendlier to the flash translation layer and cause less write amplification. The design keeps winning on modern hardware.

**2. The OS page cache does the caching**

Kafka writes to the **page cache** and lets the kernel decide when to flush to disk. It does not maintain its own in-process message cache. Two consequences:

* A JVM heap cache would mean GC pressure and duplicated data (once in heap, once in page cache). Kafka sidesteps both — the heap stays small, the cache is the OS's problem, and the OS is very good at it.
* Consumers reading recent data — which is most consumers, most of the time — are served straight out of RAM. The broker never touches the disk on that read at all. A restarted broker also keeps a warm cache, because the page cache belongs to the kernel, not the process.

This is also the setup for the next point: if the data is already sitting in a kernel page, the fastest thing you can do is never copy it into userspace.

**3. Zero-copy on the consumer path**

The normal way an app sends a file over a socket:

| Step | Copy |
| --- | --- |
| 1 | disk → page cache (kernel) |
| 2 | page cache → application buffer (**kernel → user**) |
| 3 | app buffer → socket buffer (**user → kernel**) |
| 4 | socket buffer → NIC |

Four copies, and at least two user/kernel context switches — all to move bytes the application never actually looked at.

Kafka uses the `sendfile()` syscall instead: **page cache → NIC, directly.** The data never enters the JVM. No copy into userspace, no extra context switches, no garbage created per fetch.

The reason Kafka *can* do this — and a broker like RabbitMQ largely can't — is that Kafka never inspects or transforms the message. It's an opaque byte array; there's no routing logic, no per-message header rewriting, no filtering. **The bytes on disk are exactly the bytes on the wire.** That's what makes the send a pure file-to-socket operation.

The corollary is worth remembering: anything that forces the broker to *touch* the message kills zero-copy. Classic example — a producer and consumer on mismatched message-format versions makes the broker do down-conversion, it falls back to the copy path, and throughput drops hard. Same for SSL in older setups, since encryption has to happen in userspace.

**4. Batching and compression**

Producers don't send one record per request. They accumulate records into a **batch per partition** and send the batch (`linger.ms` / `batch.size` — see [producers.md](producers.md)). That amortises the network round-trip, the request headers and the per-message overhead across hundreds of records.

Compression then applies to the **whole batch**, not per message — which compresses far better, because records in a batch tend to look alike. And the batch stays compressed end to end: the producer compresses, the broker stores and forwards the compressed batch **without decompressing it**, the consumer decompresses. The broker spends no CPU on it, and the batch stays a contiguous chunk of bytes it can hand to `sendfile()`.

**What this speed costs you**

These four choices are also the reason for most of Kafka's limitations in §4. They're the same fact seen from two sides:

* **No per-message ack** — tracking per-message state is exactly the bookkeeping sequential append avoids. You get one integer offset per consumer group instead.
* **No per-message TTL, no priority** — both require the broker to reorder or selectively delete from the middle of the log. That's random I/O, and it breaks the append-only file.
* **No content-based routing or filtering** — the broker would have to deserialize and inspect the payload, which breaks zero-copy.

So Kafka isn't fast *despite* being a dumb broker. It's fast **because** it is one — the smarts live in the producer and the consumer.

---

## 4. When *Not* to Use Kafka

This matters as much as the pros. Kafka's cost is operational complexity (see [kafka-pros-cons.md](kafka-pros-cons.md)).

* **Low volume.** A few thousand messages a day does not justify a cluster, partition planning, and consumer-group tuning. Use Redis or SQS.
* **Per-message TTL, priorities, or delayed/scheduled delivery.** Kafka has none of these. The log is strictly ordered and expires wholesale by retention. → RabbitMQ.
* **Complex routing rules** (topic/header-based routing, per-message destinations). Kafka routing is: pick a topic, pick a partition by key. → RabbitMQ exchanges.
* **Simple background job queue** (send email, resize image). You want ack-per-job, retries, dead-letter queues, arbitrary worker counts. → Celery/Redis, SQS.
* **Request/response RPC.** Kafka is one-way and asynchronous by design. → HTTP/gRPC.
* **You need to ack or delete a single message.** Kafka has no per-message ack — only "my group has read up to offset N". A poison message blocks the partition unless you handle it explicitly.
* **Strict global ordering across everything.** Only achievable with a single partition, which throws away all parallelism.

---

## 5. Which Systems Fit Kafka, and Why

**1. Event-driven microservices**
Ten services calling each other directly is up to 90 point-to-point integrations. With Kafka, each service publishes events to a topic and each interested service subscribes. Producers and consumers never know about each other — they only know the topic. Adding an eleventh service means adding one consumer, changing nothing upstream.

**2. Log and metrics aggregation**
Thousands of app instances writing logs is a high-volume, spiky, write-heavy workload with multiple destinations (search index, cold storage, alerting). Kafka absorbs the spikes as a buffer and lets every sink read the same stream at its own speed. This is literally why LinkedIn built it.

**3. Change Data Capture (CDC) and data integration**
Debezium reads the Postgres WAL → Kafka topic → Elasticsearch, data warehouse, cache invalidation, downstream services. One capture, many sinks, no dual writes and no consistency drift. See [kafka-connect.md](kafka-connect.md) — connectors mean most of this is configuration, not code.

**4. Event sourcing and audit trails**
Current state is derived by replaying events, so the log must be immutable, ordered, and durable — which is exactly what a topic is ([topics.md](topics.md)). Compliance-heavy domains (finance, healthcare) get the audit trail for free: the events are the record.

**5. IoT and telemetry ingestion**
Massive fan-in — millions of devices, small messages, extremely high write rate, ordering that only matters *per device*. Partition by device ID and you get per-device ordering plus horizontal scale.

**6. Real-time stream processing**
Fraud detection, dynamic pricing, recommendations, live dashboards — all are "compute over a continuous stream with windows and joins". Kafka Streams ([kafka-streams.md](kafka-streams.md)) and ksqlDB ([ksqldb.md](ksqldb.md)) run this on the stream directly instead of shipping data to a batch system and waiting.

---

## 6. Real-World Usage

* **LinkedIn** — built Kafka and open-sourced it in 2011 to solve activity-stream and operational-metrics ingestion. Reported at the scale of trillions of messages per day across their clusters.
* **Uber** — trip events, driver/rider location streams, dynamic (surge) pricing, fraud detection. One of the largest publicly documented deployments; they also open-sourced uReplicator for cross-datacenter replication.
* **Netflix** — the Keystone pipeline routes application and user-interaction events to real-time analytics and storage; reported in the trillions of events per day range.
* **Shopify / Pinterest** — Kafka as the central event bus feeding analytics, search indexing and ML feature pipelines.
* **Banks and fintech** — event sourcing for transaction ledgers, plus real-time fraud scoring on the transaction stream, where the immutable ordered log doubles as the audit record.
* **The generic CDC pattern** — Postgres → Debezium → Kafka → (Elasticsearch + warehouse + cache invalidation). This is probably the single most common production Kafka use case outside big tech.

> Public throughput numbers go stale fast — treat them as order-of-magnitude, not fact.

---

## 7. Top 5 Use Cases (video notes)

Overlaps §5 on purpose — §5 is "which system shapes fit", this is the ranked list as it's usually presented.

**1. Log analysis**
Centralise and analyse logs from complex distributed systems in real time. Commonly wired into the ELK stack (Elasticsearch, Logstash, Kibana), with Kafka absorbing the log volume and keeping latency low.

**2. Real-time ML pipelines**
Kafka as the central nervous system, continuously streaming data (user interactions, financial transactions) into ML models for instant fraud detection or predictive maintenance — scoring on the stream instead of waiting for a batch job.

**3. Real-time monitoring and alerting**
Central hub for infrastructure metrics. Stream processing apps continuously compute aggregates, detect anomalies, and fire alerts as the data arrives.

**4. Change Data Capture (CDC)**
Track inserts/updates/deletes in source databases and replicate them to downstream systems in real time, mostly via [Kafka Connect](kafka-connect.md) connectors.

**5. System migration**
Kafka as a buffer between old and new systems during a transition. Because the log is retained it can **replay** messages to reconcile data, so you can run both systems in parallel and migrate gradually instead of doing a big-bang cutover.

---

## 8. Decision Cheat Sheet

* **Kafka** — high volume, multiple independent consumers, replay needed, per-key ordering, stream processing, or the event log itself is the source of truth.
* **RabbitMQ** — complex routing, priorities, per-message TTL, delayed delivery, per-message ack semantics, moderate volume.
* **Redis (Streams/Lists)** — low latency, low operational cost, small scale, you already run Redis, and you can tolerate weaker durability.
* **SQS/SNS** — you're on AWS, want zero operations, and a managed queue with fan-out to queues is enough.
* **HTTP/gRPC** — you need a response back. That's not a messaging problem.
