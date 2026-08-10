# Message Queue Architecture Guide

## Scenario 1: Fan-Out (Multiple Workers Process the SAME Message)

### Redis (Streams)

* **Mechanism:** Consumer Groups.
* **Implementation:** Create a separate Consumer Group for each distinct task (e.g., `EmailGroup` and `DatabaseGroup`). When a message is published to the Stream, Redis delivers a copy to all groups. Each worker in its respective group reads and acknowledges (`XACK`) the message independently.

### AWS SNS + SQS

* **Mechanism:** Pub/Sub to Queues.
* **Implementation:** Create one SNS Topic and multiple SQS Queues. Subscribe all SQS queues to the SNS Topic. The publisher sends a message to SNS, which instantly pushes a copy to every subscribed SQS queue. Workers then poll their specific SQS queue.

### RabbitMQ

* **Mechanism:** Fanout Exchange.
* **Implementation:** Create a `Fanout` Exchange and bind multiple individual queues to it. The publisher sends the message to the Exchange, which broadcasts a copy to every bound queue. Workers consume from their assigned queues.

### Apache Kafka

* **Mechanism:** Consumer Groups.
* **Implementation:** Consumers acting on different background tasks use different `group.id` values. When a message is published to a topic, Kafka delivers it to all distinct consumer groups. Each group tracks its own offset (reading position) independently.

---

## Scenario 2: Batch Processing (Competing Workers Split a Queue)

### Redis (Streams vs. Lists — not interchangeable)

* **Mechanism:** Streams with `COUNT` and Consumer Groups, *or* Lists with `LPOP count`. These behave very differently under failure and should not be treated as two flavors of the same thing.
* **Implementation (Streams — recommended for reliable batch processing):** Multiple workers join the *same* Consumer Group. Workers call `XREADGROUP ... COUNT 50`. Redis atomically assigns the next 50 unread messages to the requesting worker, leaving them in the Pending Entries List (PEL) until acknowledged with `XACK`. If a worker crashes mid-batch, its unacked messages stay in the PEL and can be reclaimed by another worker via `XCLAIM` / `XAUTOCLAIM` — no data loss.
* **Implementation (Lists — no delivery guarantee):** Workers call `LPOP` (or `BLPOP`) to atomically pop items off a List. There is **no ack mechanism and no pending-entries concept**. The moment a worker pops a message, Redis considers it gone — if that worker crashes before finishing the work, the message is lost permanently. Lists are fine for cheap, best-effort work distribution, but should not be used where message loss is unacceptable.

### AWS SQS

* **Mechanism:** Competing Consumers with Visibility Timeout.
* **Implementation:** Multiple workers poll the exact same SQS queue using the `ReceiveMessage` API with `MaxNumberOfMessages=10`. SQS hides these messages from other workers for a specified `VisibilityTimeout`. The worker processes them and calls `DeleteMessageBatch` to remove them permanently. Standard queues don't guarantee order under concurrent competing consumers; if strict per-key ordering is required, SQS FIFO queues provide it (ordered per `MessageGroupId`) at the cost of significantly lower throughput.

### RabbitMQ

* **Mechanism:** Competing Consumers with Prefetch.
* **Implementation:** Multiple workers listen to the same queue. Each worker sets a `prefetch_count` (e.g., 50). RabbitMQ pushes up to 50 unacknowledged messages to each worker. Unacknowledged messages from a crashed worker are automatically requeued and routed to healthy workers.

### Apache Kafka

* **Mechanism:** Partition Assignment.
* **Implementation:** A Kafka topic is split into multiple Partitions. Multiple workers join the *same* `group.id`. Kafka assigns specific partitions to specific workers. A worker processes batches of messages sequentially from its assigned partition(s) and periodically commits its offset.

---

## When and Why to Choose Kafka Over the Alternatives

Kafka is fundamentally a **distributed commit log**, not just a message router. You should choose Kafka over Redis, SQS, or RabbitMQ when your architecture requires the following capabilities:

### 1. Consumer Replayability (The "Time Machine")

* **Why Kafka wins:** Kafka persists every message to disk as an append-only log, and reading a message never removes it. You can deploy a brand new service tomorrow, rewind its consumer offset to zero, and replay a year's worth of historical events exactly as they happened, with built-in tooling (offset resets, log compaction, tiered/long-term retention) designed around that workflow.
* **Nuance on Redis Streams:** Redis Streams are *technically* replayable too — messages aren't deleted on `XACK`, and any consumer can re-read from an arbitrary ID (including `0` for a full replay) until you explicitly `XTRIM` or `XDEL` them. The real gap versus Kafka is durability economics and tooling, not a hard inability to replay: Streams are backed by RAM (expensive to retain at large volume/duration) and lack Kafka's native log-compaction, tiered storage, and offset-management ecosystem. Redis Lists and Pub/Sub, by contrast, are genuinely non-replayable — messages are gone as soon as they're popped/delivered.
* **Nuance on RabbitMQ:** Classic RabbitMQ queues (as used in the competing-consumers pattern above) are destructive and ephemeral — once acked, a message is gone. However, RabbitMQ's newer **Streams** queue type (a distinct feature from Redis Streams) offers disk-backed, non-destructive, replayable reads closer to Kafka's model, so "RabbitMQ can't replay" is no longer universally true — it depends on which queue type you choose.
* **SQS:** Has no replay concept at all and caps retention at 14 days maximum.

### 2. Event Sourcing and Long-Term Storage

* **Why Kafka wins:** If your event stream *is* your database's source of truth (e.g., permanently storing every state change of a transaction), Kafka's cheap disk-based storage handles this natively. Redis is limited by expensive RAM, and SQS maxes out at a hard 14-day retention limit.

### 3. Strict Ordering at Massive Scale

* **Why Kafka wins:** Standard message queues lose strict ordering guarantees when multiple workers process messages concurrently (and SQS FIFO queues preserve ordering but have severe throughput limits). Kafka guarantees strict chronological ordering *within a partition*. By partitioning data by an entity ID (like a `user_id`), you can scale to thousands of workers while guaranteeing events for the same user are always processed sequentially by a single worker.

### 4. Stateful Stream Processing

* **Why Kafka wins:** If you need to perform real-time analytics, windowing, or joining streams on the fly (e.g., calculating a 5-minute rolling average of events before saving to a database), Kafka provides an ecosystem of native tooling designed specifically for complex stream manipulation.

### 5. Massive Throughput

* **Why Kafka wins:** Because Kafka brokers are "dumb" (they primarily just write sequential bytes to disk) and push the state-tracking complexity to the smart consumers, a cluster can scale to millions of messages per second. Traditional brokers like RabbitMQ use heavier CPU/RAM overhead to track the acknowledgment state of every individual message, causing them to bottleneck much earlier.