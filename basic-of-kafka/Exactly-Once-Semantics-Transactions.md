# Kafka: Exactly-Once Semantics (EOS) & Transactions



## The Core Problem



In distributed systems, networks drop. If a producer sends a message, but the network fails before it receives an acknowledgment, it retries. By default, this creates **duplicate messages** (At-Least-Once delivery).

**Exactly-Once Semantics (EOS)** guarantees a message is processed and saved *one time and one time only*, even if the server crashes or the network drops.

---

## How Kafka Achieves Exactly-Once



### 1. The Idempotent Producer (Stops simple retry duplicates)



Kafka assigns every producer a unique ID and tags every message with a sequence number.

* If the producer retries sending a message (e.g., Sequence #1) because it missed the ACK, Kafka sees that Sequence #1 is already saved and silently drops the duplicate.



### 2. Transactions (Atomic Consume-Transform-Produce)



For stream processing, reading a message and writing the result must succeed or fail together as a single atomic unit—similar to a relational database transaction.

---

## The Transaction Lifecycle Example



*Scenario: An application reads a $100 withdrawal (Topic A) and writes a $100 deposit (Topic B).*

1. **Consume (The Read):** The application reads the `$100 withdrawal` from Topic A.


2. **Begin Transaction:** The app tells Kafka to start an atomic transaction.


3. **Produce (The Write):** The app writes the `$100 deposit` to Topic B. *(Note: Kafka accepts this but hides it from consumers, marking it as "uncommitted").*


4. **Update State (The Bookmark):** The app tells Kafka to update its consumer offset, marking the withdrawal from Step 1 as "read". *(Note: Because it's in a transaction, this offset update is also "uncommitted" and not finalized yet).*


5. **Commit (The Finalize):** The app says "Commit!" Kafka instantly does two things simultaneously:


* Makes the deposit on Topic B visible to the world.


* Finalizes the offset on Topic A so the withdrawal is permanently marked as read.





---

## What Happens on a Crash?



If the application crashes at **Step 4** (before committing):

* Kafka **aborts** the transaction automatically.


* It throws away the hidden deposit on Topic B.


* It throws away the uncommitted offset update on Topic A.


* When the application restarts, it reads the original withdrawal again and safely retries from scratch. No duplicates, no lost data.