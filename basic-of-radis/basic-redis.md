# The Ultimate Guide to Redis Scaling: From Single Node to Cluster on AWS

## Part 1: Fundamentals

### What is Redis and Why Use It?

Redis (Remote Dictionary Server) is an in-memory data structure store. Unlike a traditional relational database (PostgreSQL/MySQL) that writes to disk (which is slow), Redis keeps data in RAM (which is blazing fast).

**Common Use Cases:**

1.  **Caching:** Storing HTML or API responses to reduce database load.
2.  **Session Storage:** Managing user login tokens across servers.
3.  **Pub/Sub:** Real-time chat and notifications.
4.  **Leaderboards:** Using Sorted Sets for gaming scores.
5.  **Task Queues:** Managing background jobs (Celery/Bull).

-----

## Part 2: The Scaling Hierarchy

Scaling Redis isn't one-size-fits-all. It follows a progression based on load and data size.

### Level 1: Vertical Scaling (The "Bigger Box")

  * **Method:** Upgrade your EC2 instance (e.g., `t3.micro` → `r6g.large`).
  * **Pros:** Zero config changes.
  * **Cons:** Hard limit on RAM; Single Point of Failure (SPOF).

### Level 2: Replication (Read Scaling)

  * **Architecture:** 1 Master (Writes) + N Replicas (Reads).
  * **How it works:** Master asynchronously syncs data to replicas.
  * **Load Balancing:** Redis **does not** load balance itself. Your Client (Django) or a Proxy (HAProxy) must decide where to send traffic.

### Level 3: Redis Cluster (Write & Size Scaling)

  * **Architecture:** Multiple Masters (Sharding) + Replicas.
  * **How it works:** Data is split into 16,384 "Hash Slots."
  * **Failover:** Automatic (Gossip protocol).

-----

## Part 3: Implementing Master-Replica with High Availability

This is the standard setup for most production applications (up to \~100k writes/sec).

### 1\. The Architecture

  * **Redis Tier:** 3 EC2 instances.
      * Node A: Master + Sentinel
      * Node B: Replica + Sentinel
      * Node C: Replica + Sentinel
  * **Proxy Tier:** 1 HAProxy EC2 instance.
  * **App Tier:** Django EC2 instances.

### 2\. High Availability (Sentinel)

We use **Redis Sentinel** to monitor the Master. If the Master dies, Sentinels vote and promote a Replica to be the new Master.

  * **Config:** Run `redis-sentinel` on odd-numbered servers (usually 3).

### 3\. Load Balancing with HAProxy

We use HAProxy to abstract the complexity. Django sees one IP, but HAProxy routes traffic based on roles.

**Why HAProxy?**
Standard clients (like `django-redis`) struggle to load balance reads effectively while handling failover. HAProxy handles this via **TCP Checks**. It asks Redis `INFO replication` to see who is Master and who is Slave.

**The `haproxy.cfg` Configuration:**
We open two ports: **6379 for Writes** and **6380 for Reads**.

```haproxy
frontend redis_write
    bind *:6379
    default_backend redis_master
frontend redis_read
    bind *:6380
    default_backend redis_slaves

backend redis_master
    option tcp-check
    # Only send traffic to the node saying "role:master"
    tcp-check expect string role:master
    server redis1 10.0.0.1:6379 check
    server redis2 10.0.0.2:6379 check
    server redis3 10.0.0.3:6379 check

backend redis_slaves
    balance roundrobin # <--- READ SCALING
    option tcp-check
    # Only send traffic to nodes saying "role:slave"
    tcp-check expect string role:slave
    server redis1 10.0.0.1:6379 check
    server redis2 10.0.0.2:6379 check
```

**Django Configuration:**
Django connects to the HAProxy IP (`10.0.0.100`).

```python
CACHES = {
    "default": { # Writes
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://10.0.0.100:6379/1",
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"}
    },
    "read_cache": { # Reads
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://10.0.0.100:6380/1",
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"}
    }
}
```

### 4\. Alternatives to HAProxy?

  * **Nginx:** Not recommended for Free users. It lacks the ability to perform dynamic TCP checks (checking `role:master`), meaning manual updates are required during failover.
  * **AWS ELB (ALB/NLB):** Not recommended. ALB is HTTP only. NLB is "blind" to Redis roles and causes write errors by sending writes to read-replicas.
  * **AWS ElastiCache:** If you use this, you **don't** need Sentinel or HAProxy. AWS manages the failover and provides a DNS Endpoint for Primary (Write) and Reader (Read).

-----

## Part 4: Implementing Redis Cluster (Massive Scale)

Use this when your data \> RAM limit or Write load \> 1 Master's CPU.

### 1\. How Sharding Works

Data is split across **Hash Slots**.

  * Master A holds slots 0-8191.
  * Master B holds slots 8192-16383.
  * The Client (Django) calculates `CRC16(key) % 16384` to find the right server.

### 2\. Architecture: 2 Masters, 4 Replicas

  * You run `redis-cli --cluster create` to set up the mesh.
  * **Failover:** Built-in. If Master A dies, the other nodes vote to promote Replica A1. **No Sentinel is needed.**

### 3\. Django Configuration (Smart Client)

We do **not** use HAProxy here. A proxy blinds the client to the sharding map. We use `django-redis` with `RedisClusterClient`.

```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        # List multiple "Seed Nodes" for robustness
        "LOCATION": [
            "redis://10.0.0.1:6379/0",
            "redis://10.0.0.2:6379/0",
        ],
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.RedisClusterClient",
            "REDIS_CLIENT_KWARGS": {
                # Critical: Allows reading from the 4 replicas
                "read_from_replicas": True,
            }
        }
    }
}
```

### 4\. How Cluster Load Balancing Works

  * **Writes:** Routed strictly to the Master owning the slot.
  * **Reads:** If `read_from_replicas=True`, the client identifies the "Shard Family" (e.g., Master A + Replica A1 + Replica A2) and randomly selects one.
  * **Least Connections:** Not supported natively by `django-redis`. Requires a smart sidecar proxy like **Envoy** if strictly needed.

-----

## Part 5: Real-World Workload Segmentation

In a complex production system handling Caching, Pub/Sub, and Queues, **do not use a single Redis instance.** They have conflicting eviction requirements.

### The Recommended "3-Cluster" Strategy

1.  **Caching Cluster (Redis Cluster):**

      * **Goal:** Massive memory.
      * **Policy:** `allkeys-lru` (Delete old data when full).
      * **Scaling:** Horizontal (Add shards).

2.  **Task Queue Cluster (Master+Replica+Sentinel):**

      * **Goal:** Reliability (Don't lose jobs).
      * **Policy:** `noeviction` (Error if full, never delete).
      * **Persistence:** AOF enabled (`fsync everysec`).

3.  **Pub/Sub Cluster (Master+Replica+Sentinel):**

      * **Goal:** Low Latency / High Network throughput.
      * **Policy:** `volatile-ttl`.
      * **Isolation:** Ensures chat traffic doesn't block background workers.

-----

## Part 6: Summary & Decision Matrix

**Which approach should you choose?**

| Scenario | Recommended Architecture |
| :--- | :--- |
| **Simple App / Low Budget** | Single EC2 (Vertical Scaling) |
| **Production Standard (HA)** | Master + Replicas + Sentinel + HAProxy |
| **Managed / No Ops Team** | AWS ElastiCache (Cluster Mode Disabled) |
| **Massive Data / Heavy Writes** | Redis Cluster (Direct Client Connection) |
| **Complex Mixed Workload** | Segregate into 2 or 3 separate Redis setups |

### Final "Golden Rules"

1.  **Never** use AWS NLB for Redis; it causes Write-to-Replica errors.
2.  **Never** mix Sentinel with Redis Cluster; they will conflict on failover logic.
3.  **Always** use HAProxy if you want effective Read-Balancing with a Sentinel setup.
4.  **Always** use the Direct `RedisClusterClient` (without Proxy) for Redis Cluster to minimize latency and handle redirections correctly.


In Redis sentinal or cluster scaling has common porblem is split brain problem. To make either system robust against split-brain, you must always deploy an odd number of voting instances (e.g., 3 Sentinels or 3 Master nodes in a cluster) across independent failure domains (e.g., different AWS Availability Zones).


















# sync and async redis

# redis streams
