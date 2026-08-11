# Kafka — Pros & Cons

## Pros

- **Append-only commit log** — writes are sequential, nothing is updated in place. Cheap writes, and messages stay readable after being consumed (replay is possible).
- **Very fast** — sequential disk I/O + zero-copy + batching. Throughput is measured in millions of messages/sec, not thousands.
- **Distributed by design** — data lives in partitions spread across brokers, with replication for fault tolerance. A broker dying doesn't lose data.
- **Horizontal scaling** — add brokers to scale storage/throughput, add partitions to scale consumption. No rewrite needed.
- **Parallel processing** — one partition = one consumer in a group. More partitions = more consumers working at once.
- **Both pub/sub and queue** — many consumer groups each get all messages (pub/sub); consumers inside one group split the messages (queue).
- **Long polling** — consumers pull and wait instead of hammering the broker, so low latency without wasted requests.
- **Durable retention** — messages are kept by time or size, independent of consumption. New consumers can read history from offset 0.
- **Decoupling** — producers and consumers don't know about each other; a slow or dead consumer doesn't block producers.

## Cons

- **Complex to install, configure and manage** — brokers, replication, partitions, retention, and consumer-group tuning are all things you must get right yourself.
- **Operationally heavy** — needs monitoring (lag, ISR, disk), capacity planning, and disks. Not a "just run it" component.
- **Ordering only within a partition** — global ordering across a topic is impossible unless you use a single partition (which kills parallelism).
- **Partition count is hard to shrink** — you can add partitions, but that reshuffles key→partition mapping and breaks per-key ordering.
- **No per-message features** — no priority queues, no per-message TTL, no selective ack/delete like RabbitMQ or SQS.
- **At-least-once by default** — duplicates happen on retries/rebalances; consumers must be idempotent (exactly-once needs transactions and costs performance).
- **Overkill for small workloads** — for low volume or simple task queues, Redis/RabbitMQ/SQS is far less work.
- **Rebalances hurt** — when a consumer joins or leaves, the group pauses while partitions are reassigned.

## Rule of thumb

Use Kafka when you need **high-throughput, durable, replayable event streams** consumed by **multiple independent systems**. Skip it when you just need a simple background job queue.
