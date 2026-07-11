---
title: "What Really Happens When You Make a gRPC Request"
subtitle: "Every guide told me the what and why of gRPC. None showed me the how — so I built a demo and traced a request from client to server, and back."
date: 2026-07-11
type: article
tags: [grpc, backend, http2, protobuf, distributed-systems]
---

## Where This Started

Recently at work I was handed a project that needed gRPC. As a backend developer I already had solid experience with REST and GraphQL, but I'd never touched gRPC before — so I was excited to learn it and ship it in a real, production-grade system. Naturally, I searched first: Google, AI, the official docs, a pile of blog posts. And everywhere I looked I found the same thing — *what is gRPC*, *what is RPC*, *why use it over REST*. All useful, all high-level, and after reading all of it I still had one nagging problem: **I didn't actually understand how gRPC works under the hood.**

So I stopped reading and started building. I put together a small demo — similar to my real assignment but stripped down to a few features — and traced what happens from the moment a request leaves the client until the response comes back. That's when it clicked, and that's what this article is about.

> 🔗 *Project link goes here — you can explore the code yourself.*

## So, What Is gRPC?

gRPC is a high-performance RPC (Remote Procedure Call) framework: calling a method on a remote server should feel like calling a plain function — you call `getUser(id)` and gRPC serializes the arguments, sends them over the network, and hands back a typed response. Under the hood it's built on **HTTP/2** for transport and **Protocol Buffers** for serializing messages.

It pays off in a **microservice architecture**, where services call each other constantly and those internal calls care more about latency, throughput, and a strict shared contract than human-readable payloads. That's also what sets it apart from **REST**: REST models resources over JSON on HTTP/1.1, while gRPC models method calls over binary Protobuf on HTTP/2 — smaller payloads, built-in streaming both ways, and client/server stubs generated from one `.proto` contract instead of hand-written HTTP clients.

## The Pieces You Need to Know First

Before we can trace a request end to end, there are a few concepts gRPC is built on. The lifecycle doesn't make sense without them, so here's each in a sentence or two.

**HTTP/2** — gRPC doesn't invent its own transport; it rides on HTTP/2. That's what lets it carry many requests over one connection at once (multiplexing), push data both ways, and stream messages without waiting for the previous call to finish. Almost everything fast about gRPC traces back to this.

**Protocol Buffers (Protobuf)** — how you define your messages and serialize them onto the wire. Instead of human-readable JSON, gRPC sends a compact binary format described by a `.proto` file — the contract both sides generate code from, so they always agree on the shape of the data.

**Channel** — the client's long-lived connection to a service. You create one and reuse it for many requests instead of connecting per call; it manages the underlying connections and their state for you.

**Name Resolver** — a service is usually addressed by a name (like a DNS hostname), not a raw IP. The resolver turns that name into a concrete list of addresses to connect to — and it can return many backends, not just one.

**Subchannel** — if a channel is the connection to a *service*, a subchannel is the connection to a *single* backend behind it. When the resolver returns several addresses, the channel creates one subchannel per address.

**Load Balancing** — when there are multiple backends, something decides which one each call goes to. It sits between the channel and its subchannels, spreading calls across healthy backends and routing around ones that go down.

**TCP Connection** — under the channels, subchannels, and HTTP/2 framing is still a plain TCP socket moving the actual bytes. Worth remembering when a connection drops or a request stalls.

**Interceptors** — gRPC's middleware. They hook into a call as it passes through — client and server side — for cross-cutting concerns like logging, auth, metrics, or retries. Write the logic once; it runs around every call.

**Stub** — the client-side handle you call methods on. Calling a remote method looks just like a local function call — that illusion is the stub's job. Under the hood it serializes your arguments and sends them through the channel.

**Servicer** — the other half: the server-side implementation that answers calls. You define the service in the `.proto`, gRPC generates a base class, and you implement its methods. When a request arrives, gRPC routes it to the matching one.

With those in hand, the request/response cycle stops being magic.

## A Full Request/Response Cycle: 1 Client, 2 Servers

Here's a concrete scenario from my own project. The client is `order-service`, calling the `InventoryService` defined in my `.proto` — specifically the unary `ReserveStock` RPC:

```proto
service InventoryService {
  // Atomically reserve stock for an order, all-or-nothing.
  rpc ReserveStock(ReserveStockRequest) returns (ReserveStockResponse);
}

message ReserveStockRequest {
  string order_ref = 1;
  repeated ReserveItem items = 2;
  string idempotency_key = 3;  // makes a retry safe against double-reserving
}
```

The `inventory-service` runs on **two instances** — `10.0.0.1:50051` and `10.0.0.2:50051`, both behind one name `inventory-service:50051`. Here's what actually happens.

### Phase 1 — Setup (happens once, triggered by the first call)

The channel is **lazy**. `order-service` creates the channel object at boot, but that does nothing on the network — no resolution, no connections. Everything below is kicked off by the **first RPC**, then reused for every call after it.

**1. Create the channel — at startup.** `order-service` points a channel at `inventory-service:50051`. Nothing is connected yet; the channel just holds the target.

**2. The first RPC triggers name resolution.** The resolver looks up `inventory-service` and returns *both* addresses. Now the channel knows there are two backends, not one.

**3. A subchannel per backend.** One subchannel for `10.0.0.1`, one for `10.0.0.2`. Each opens a **TCP connection** and negotiates **HTTP/2** to its server.

**4. Load balancing kicks in.** Here's a detail worth knowing: gRPC's *default* policy is `pick_first`, which sends **all** traffic to one backend. To actually spread calls across both servers you configure `round_robin` — which then alternates: server 1, server 2, server 1, and so on.

From here, the channel, subchannels, and connections stay alive and get reused. Steps 2–4 don't repeat — only the per-call steps below do.

### Phase 2 — Per Call (repeats for every request)

**5. Call the stub** — `stub.ReserveStock(ReserveStockRequest(order_ref="ord-42", items=[...], idempotency_key="ord-42"))`. In `order-service`'s code it looks like a normal function call.

**6. Client interceptors run.** Logging, auth, or metrics fire here and can attach metadata (like an auth token) to the outgoing call.

**7. Protobuf serializes the request.** The `ReserveStockRequest` becomes a compact binary blob.

**8. Load balancer picks a subchannel.** Say it's server 1's turn — the call routes to the `10.0.0.1` subchannel.

**9. The call travels as an HTTP/2 stream.** gRPC opens a new stream on that server's existing connection and sends the bytes. Because HTTP/2 multiplexes, other calls share the same connection at the same time.

**10. Server 1 receives and decodes.** Its HTTP/2 layer hands the bytes up, Protobuf deserializes them back into a `ReserveStockRequest`, and server-side interceptors run.

**11. The servicer handles it.** gRPC routes the request to the `ReserveStock` method, which reserves the stock (checking the `idempotency_key` so a retry doesn't reserve twice) and returns a `ReserveStockResponse`.

**12. The response returns the same way** — serialized, back over the same HTTP/2 stream, through the client interceptors, deserialized, and handed to `order-service` as a normal return value.

**13. The next call goes to server 2.** Round-robin sends the next `ReserveStock` to the `10.0.0.2` subchannel — reusing its already-open connection. No new resolution, no new handshake. That reuse is why the setup phase only happens once.

And if server 1 goes down? Its subchannel notices the dropped connection, marks itself unhealthy, and the load balancer stops routing to it — sending everything to server 2 until it recovers. The client code never changes.

## Conclusion

The point isn't to repeat what gRPC is — it's that "what" and "why" aren't enough when you're building something real. Once you can trace a single call through the channel, resolver, a load-balanced subchannel, an HTTP/2 stream, and back, gRPC stops being a black box.

That same understanding is what makes it production-ready, because most best practices just protect one step of that cycle: reuse **one channel per service** (setup is expensive, reuse is cheap), add a **channel pool** when you outgrow one connection's stream limit, and use **keepalive** to catch silently dropped connections. For reliability, put a **deadline** on every RPC, keep **retries** idempotent with backoff (why our `ReserveStock` carries an `idempotency_key`), and **rate-limit** noisy clients. To stay trustworthy: **TLS/mTLS** for encryption and identity, the **right status codes** so clients retry `UNAVAILABLE` but not `INVALID_ARGUMENT`, and **observability** from interceptors so you can see where a slow request goes.

That's the difference between a working demo and a production-grade system. Next up: the three streaming modes — client, server, and bidirectional — which are just variations on this same cycle.

*To be continued.*
