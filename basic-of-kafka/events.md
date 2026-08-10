# Events — the atom of Kafka

> Everything else in Kafka (topics, partitions, keys, schema registry) only makes sense once the event model is clear. Start here.

---

## What is an event?

**An event is a thing that happened.** Past tense, already done, cannot be un-happened.

That's not a pedantic point — it's the whole mental model. A command says *"do this"* and can be rejected. An event says *"this occurred"* and can only be recorded.

Examples:

* user clicked checkout
* sensor read 24.3°C
* order status changed to `shipped`
* microservice produced an output

**Remember it as:** *events are facts, not requests.* That's why they're immutable, and why the log can be an audit trail.

---

## An event is a key-value pair

Kafka models every event as:

```text
key   → who/what this event is about   (order_id, user_id, device_id)
value → what actually happened          (the payload)
```

Plus two things that are easy to forget:

```text
timestamp → when (set by producer or broker)
headers   → metadata (trace id, source, content type) — not part of the payload
```

### The key is optional, and that choice matters

| Key | What happens | Use when |
| --- | --- | --- |
| **Set** | `hash(key) % partitions` → always the **same partition** → **ordering guaranteed per key** | You need per-entity order (all events for `order_42` in sequence) |
| **null** | Spread round-robin / sticky across partitions | You just want throughput, order doesn't matter |

**Remember it as:** *the key is not an ID, it's a routing decision.* Picking the key = picking your ordering guarantee. See [partitioning.md](partitioning.md).

Keys are often primitives (string, int), but can be complex domain objects.

---

## Kafka is loosely typed — internally it's just bytes

When an event is actually stored, **key and value are both just byte sequences.** The broker has no idea whether it's JSON, Avro, Protobuf, or garbage. It never parses your data.

Consequences worth remembering:

* **Fast** — no parsing, no validation, no per-message inspection on the broker. It just appends bytes to disk.
* **Serialization is the client's job** — producers serialize, consumers deserialize. If they disagree on format, the broker won't warn you; the consumer just breaks.
* **This is exactly why [schema-registry.md](schema-registry.md) exists.** Since the broker won't enforce a contract, something else has to. The registry sits outside the broker and validates schemas on the client side.

**Remember it as:** *the broker is a dumb pipe on purpose.* Dumb broker = fast broker. Intelligence lives in the clients.

---

## Quick recall

| Question | Answer |
| --- | --- |
| What is an event? | A fact — something that already happened |
| How is it modeled? | key + value (+ timestamp, headers) |
| What does the key control? | Which partition → therefore ordering |
| What if the key is null? | Round-robin, no ordering guarantee |
| What does the broker know about your data? | Nothing. Bytes only |
| Why does Schema Registry exist? | Because the broker enforces no types |

**Next:** [topics.md](topics.md) → where events are stored · [partitioning.md](partitioning.md) → how the key splits them · [why-and-when-kafka.md](why-and-when-kafka.md) → why use Kafka at all
