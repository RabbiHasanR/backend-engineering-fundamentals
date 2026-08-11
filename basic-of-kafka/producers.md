# Producers — who writes into the log

> A **producer** is a client application that appends events to a topic.
> It is *your* code plus the Kafka client library — not a Kafka server process.

**Remember it as:** *the producer decides **which partition** the event lands in, and **when the write counts as done**.*

---

## What a producer is responsible for

Every `produce()` call walks through these five steps inside the client library:

| Step | What happens | Knob |
| --- | --- | --- |
| **1. Serialize** | Python object → bytes (JSON, Avro, Protobuf) | serializer / [schema-registry.md](schema-registry.md) |
| **2. Pick a partition** | `hash(key) % partition_count`, or round-robin if no key | the **key** you pass |
| **3. Batch & compress** | Buffer in memory, group messages per partition | `linger.ms`, `batch.size`, `compression.type` |
| **4. Send & retry** | One TCP connection per broker, reused; retry on failure | `retries`, `enable.idempotence` |
| **5. Wait for the ack** | Broker confirms the write; then the callback fires | `acks` |

Steps 3–5 are why a producer object is expensive: **create one per service and reuse it**. Creating a producer per request throws away the connections and the batching.

---

## Minimal example

```python
import json
from confluent_kafka import Producer

producer = Producer({
    "bootstrap.servers": "broker1:9092,broker2:9092",
    "acks": "all",
    "enable.idempotence": True,
    "linger.ms": 10,
    "compression.type": "lz4",
})

def on_delivery(err, msg):
    """Fires once the broker has acked — or failed."""
    if err:
        print(f"FAILED: {err}")          # your problem now: log it, retry, dead-letter
    else:
        print(f"ok → partition {msg.partition()} offset {msg.offset()}")

producer.produce(
    topic="ticket_purchased_events",
    key="seat_A17",                       # routing key → decides the partition
    value=json.dumps({"seat_id": "seat_A17", "user_id": 42}).encode(),
    callback=on_delivery,
)

producer.flush()                          # block until everything buffered is sent
```

**`produce()` does not send anything.** It only puts the message into the in-memory buffer and returns immediately. A background thread does the real sending. That's why the result arrives in `on_delivery`, and why `flush()` exists.

---

## How the partition is chosen

```text
key="seat_A17"  ──hash──►  P2   ─┐
key="seat_A17"  ──hash──►  P2   ─┤ same key → same partition → ordered
key="seat_B03"  ──hash──►  P0    │
key=None        ──round-robin──► P0 P1 P2 P3   (spread out, no ordering)
```

- **Order is only guaranteed inside one partition.** So key by the entity whose history must stay in order — `seat_id`, `user_id`, `order_id`.
- **No key = no ordering guarantee**, but even load across partitions.
- Adding partitions later re-maps the hash → an existing key can move to a different partition. See [partitioning.md](partitioning.md).

---

## Batching — the throughput dial

| Setting | Meaning | Effect |
| --- | --- | --- |
| `linger.ms` | Wait this long to collect more messages before sending | ↑ = bigger batches, more throughput, more latency |
| `batch.size` | Max bytes per batch, per partition | Send fires when either limit hits first |
| `compression.type` | `lz4` / `snappy` / `zstd` | Compresses the *whole batch* → bigger batch = better ratio |

One sentence to remember: **`linger.ms` trades latency for throughput.** `0` = send immediately (lowest latency). `10–100` = far fewer network round-trips. Batches are compressed once and stay compressed on disk and on the wire to consumers.

---

## `acks` — the durability dial

| `acks` | Producer waits for | You lose data when | Use for |
| --- | --- | --- | --- |
| `0` | nothing — fire and forget | anything at all goes wrong | metrics, logs you can drop |
| `1` | leader wrote it | leader crashes before followers copy it | "fast and mostly safe" |
| `all` | leader **+ all in-sync replicas (ISR)** | only if all replicas die | money, orders, anything you can't lose |

`acks=all` is only as strong as `min.insync.replicas` on the broker — that setting decides how many ISR members must confirm. See [replication.md](replication.md).

---

## Retries and duplicates

A retry is not free: the first attempt may have *succeeded* and only the ack got lost. Retrying then writes the message twice.

```python
"enable.idempotence": True    # turn this on
```

Idempotence gives each producer a producer-ID + sequence number, so the broker recognises and drops a re-sent duplicate. It also **preserves order** during retries — without it, a retried message can land *after* a later one.

> Beyond that: **transactions** (`transactional.id` + `begin/commit_transaction`) give exactly-once across multiple topics. Rarely needed — idempotence covers most cases.

---

## When you need this

- **Not calling `flush()` before shutdown** → whatever is still in the buffer is silently lost. Always `flush()` on exit.
- **Creating a `Producer` per request** → no batching, connection churn. One per service, reused.
- **Ordering suddenly broken** → you forgot the key, or turned off idempotence with retries on.
- **`acks=1` and a leader crash** → the write vanishes and nobody errors. Use `acks=all` for critical events.
- **Latency-sensitive path feels slow** → check `linger.ms`; you may be waiting for a batch that never fills.
- **The callback is your only error signal** — a bare `produce()` with no callback fails silently.

---

## Related

- [events.md](events.md) — what you actually put in `value`
- [topics.md](topics.md) — where the message lands and how offsets work
- [partitioning.md](partitioning.md) — keys, hashing, and parallelism
- [replication.md](replication.md) — ISR, `min.insync.replicas`, what `acks=all` really waits for
- [consumers.md](consumers.md) — the other side of the log
- [schema-registry.md](schema-registry.md) — serialization done properly
