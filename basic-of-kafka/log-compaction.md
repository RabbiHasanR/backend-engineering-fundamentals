# Log Compaction & Tombstones — keeping state, not history

> **Compaction** is a retention policy that deletes a record only when a *newer record with the
> same key* exists. **A tombstone** is a record with a real key and a `null` value — the only way
> to tell a compacted topic "this key is gone".

**Remember it as:** *time retention answers "how old is it?", compaction answers "is it still the
latest for its key?"*

---

## The problem compaction solves

Time retention throws away data by age. That's wrong whenever the topic represents **current
state** rather than a stream of facts:

- `users.profile` — the last profile update for a user must survive forever, even if it was
  written three years ago.
- `products.price` — a service booting today needs *every* product's current price, not the ones
  that happened to change this week.

With `retention.ms` you must choose between infinite retention (unbounded disk, replaying years
of history on every restart) and losing state. Compaction gives you the third option: **bounded
disk, complete state.**

```text
before:  (user1, A) (user2, X) (user1, B) (user1, C) (user2, Y)
after:   (user1, C) (user2, Y)
```

Guarantee: a consumer reading the whole topic from offset 0 always ends up with the correct
latest value for every key. It may or may not see the intermediate versions.

---

## How the cleaner actually works

The log is split into segments. Only the **active segment** (the one currently being appended to)
is ever written; everything behind it is immutable.

| Region | Name | State |
| --- | --- | --- |
| Newest, still being appended | **head** / active segment | Never compacted — every version still present |
| Everything older | **tail** | Cleaned — at most one record per key |

A background thread (the **log cleaner**) builds an in-memory map of `key → highest offset` over
the tail, then rewrites those segments keeping only records at their winning offset.

Three consequences that trip people up:

1. **Compaction is asynchronous and best-effort in timing.** Duplicates for a key can be visible
   for a long time. Never write a consumer that assumes "one record per key".
2. **Offsets are preserved, not renumbered.** Compacted logs have *gaps* — offset 5 may simply
   not exist. Consumers must tolerate that.
3. **Ordering per key is preserved.** Compaction removes records, it never reorders them.

---

## Records without a key are a bug

Compaction is keyed by definition. A `null`-key record on a compacted topic can never be
superseded and can never be cleaned — **producing keyless records to a compacted topic is a
configuration error**, not a style choice. (See [partitioning.md](partitioning.md) — the key is
also what pins a key's whole history to one partition, which is what makes "latest wins"
well-defined.)

---

## Tombstones — how a key gets deleted

Compaction alone can only *replace* a value. To express deletion you produce a record with the
key and a **`null` value**:

```text
(user1, C) (user2, Y) (user1, null)   ← tombstone
```

The tombstone is a normal record: it's appended, replicated, and read by consumers like any
other. Downstream consumers are expected to interpret `value == null` as *delete this key from
your local state*.

The cleaner then does two passes:

1. It removes all **earlier** records for that key — normal compaction.
2. After a grace period it removes **the tombstone itself**, and the key vanishes from the topic
   entirely.

### Why the grace period exists

That delay is `delete.retention.ms` (**default 24 hours**). Without it a slow or offline consumer
could read the old value, then have the tombstone deleted before it got there — and would keep a
deleted key in its state forever. The window is the promise: *any consumer that catches up within
this time is guaranteed to see the delete.*

**The trap:** a consumer that is down longer than `delete.retention.ms` and then does a full
re-read will resurrect deleted keys. If your consumers can lag for days, raise this.

---

## Configuration worth knowing

| Config | Meaning | Default |
| --- | --- | --- |
| `cleanup.policy=compact` | Compaction instead of age-based deletion | `delete` |
| `cleanup.policy=compact,delete` | Both — compact *and* drop anything past `retention.ms` | — |
| `delete.retention.ms` | How long tombstones stay readable | 24 h |
| `min.cleanable.dirty.ratio` | How much uncompacted data before cleaning starts | 0.5 |
| `min.compaction.lag.ms` | Minimum age before a record is eligible | 0 |
| `max.compaction.lag.ms` | Upper bound on how long a record can sit uncompacted | ∞ |
| `segment.ms` / `segment.bytes` | How fast the head rolls into the cleanable tail | 7 d / 1 GB |

Two practical notes:

- **`min.cleanable.dirty.ratio=0.5`** means the log can be up to ~50% garbage before the cleaner
  bothers. Lower it for tighter disk usage, at the cost of more I/O.
- **The active segment is never compacted**, so on a low-traffic topic a record can linger for
  `segment.ms` (7 days) before it's even *eligible*. If you need timely deletes — GDPR, for
  instance — you must lower `segment.ms` and `max.compaction.lag.ms`; the defaults do not give
  you a deletion SLA.

`compact,delete` is the combination you want when state is keyed but genuinely expires — a
session store, for example: latest value per session, and nothing older than a day regardless.

---

## Where you'll actually meet it

- **`__consumer_offsets`** — Kafka's own internal topic is compacted, keyed by
  `(group, topic, partition)`. That's how a group's committed offset survives indefinitely
  without storing every commit ever made. See [consumers.md](consumers.md).
- **KRaft metadata** — the same "keep the latest, drop the history" idea, done with snapshots
  instead of the cleaner. See [kraft-controller.md](kraft-controller.md).
- **Kafka Streams `KTable` / changelog topics** — every state store is backed by a compacted
  changelog so a restarted instance can rebuild its state by replaying it. See
  [kafka-streams.md](kafka-streams.md).
- **CDC / outbox topics** — keyed by primary key, so the topic mirrors the table's current rows.
  A row `DELETE` becomes a tombstone. See [kafka-connect.md](kafka-connect.md).

---

## When you need this

- **"My topic grows forever but I only care about current values"** → `cleanup.policy=compact`.
- **"I deleted the record but consumers still have it"** → you produced no tombstone, or a
  consumer that ignores `null` values, or a consumer lagged past `delete.retention.ms`.
- **"Deleted keys came back"** → a consumer re-read the topic after the tombstones were cleaned.
- **"I see two values for one key"** → compaction hasn't run yet (head segment, or dirty ratio not
  reached). Expected — your consumer must be last-write-wins.
- **"Compaction never runs"** → check `min.cleanable.dirty.ratio` and whether the data is still
  sitting in the active segment.
- **Never repartition a compacted topic** — old values for a moved key are stranded in the old
  partition and you end up with two live values for one key. See
  [partitioning.md](partitioning.md).

---

## Related

- [topics.md](topics.md) — retention modes and where compaction sits among them
- [partitioning.md](partitioning.md) — why the key must stay on one partition
- [events.md](events.md) — key vs value, and why keys aren't optional here
- [consumers.md](consumers.md) — `__consumer_offsets`, the compacted topic you already use
- [kafka-streams.md](kafka-streams.md) — KTables and changelog topics built on compaction
