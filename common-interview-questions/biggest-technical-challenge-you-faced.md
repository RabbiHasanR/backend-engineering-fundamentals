# Biggest Technical Challenge I Faced

## Context

I work at a sports-tech company that builds a real-time scoring and streaming platform for sports like cricket, football, and baseball. When a match is created and starts, a scorer inputs live scores, and every connected user must see score updates, match info, notifications, and other live events in real time. We also run a live video stream alongside the scoreboard, so latency and reliability are critical to the product experience.

To handle this real-time data flow, we built a dedicated WebSocket service.

## The Problem

The original WebSocket service was a legacy implementation written in Python , Django , Django Channels, Redis. During our pilot and pre-release testing, we discovered serious issues:

- The service could not reliably handle even 300–500 concurrent users.
- WebSocket connections were dropping frequently, even when the network was healthy.
- We had no observability — no metrics, no structured logs, no way to know why connections failed or how many were active.
- Because real-time updates are core to our product, this effectively blocked the pilot.

Management had planned to release the system right after the pilot, so the failure had high visibility and high stakes. The original developers (an ex-employee and a junior engineer) were no longer available, and the rest of the team was committed to other services. I was assigned to fix it solo, with a tight one-month deadline.

I had worked with WebSockets before, but never on a legacy system at this scale and under this kind of time pressure — so this stands out as the biggest technical challenge I have faced recently.

## Diagnosis

I started by mapping out everything that could be wrong, end-to-end. I found multiple compounding issues:

1. Connection fan-out per user — Each client opened 6–7 separate WebSocket routes. With 500 users, that meant ~3,500 live connections, which alone was overwhelming the server.
2. Heavy work inside consumers — The WebSocket consumers were doing DB reads *and* writes, even though this service should only fan out messages.
3. Django's footprint — Django is sync-first, memory-heavy, and depends on Django Channels as an extra abstraction for pub/sub. In our setup, each live WebSocket connection was costing roughly [X] MB of memory under Django Channels, which multiplied very quickly across thousands of connections. For a high-connection, low-CPU workload, it was the wrong tool.
4. Timeout chain across layers — The service ran behind Cloudflare → Nginx → Daphne on an EC2 instance. Every layer had idle/HTTP timeouts tuned for normal HTTP traffic, which kept killing long-lived WebSocket connections.
5. Inefficient Redis usage — Each Redis command opened a connection, executed, and closed it instead of reusing connections or batching with pipelines.
6. No observability — No metrics on active connections, handshake duration, disconnect reasons, or message throughput. Debugging was guesswork.
7. Undersized infra — The host was a t2.small EC2 instance whose RAM was saturated at 500–600 concurrent users, mostly because of Django's memory profile multiplied across workers and connections.

## Decision and Trade-offs

After analyzing the root causes, I proposed a rewrite rather than patching. My plan:

- Rewrite the service in FastAPI. FastAPI is async-native, has a low memory footprint, starts fast, and gives much lower latency than Django for I/O-bound workloads like WebSockets. I primarily code in Python and had already built several production services with FastAPI, so I was confident I could move fast without learning a new stack mid-crisis. Staying in Python also meant the rest of the team could maintain the service afterward.
- Single multiplexed route per client. Instead of 6–7 routes per user, one connection carries all message types, dispatched by a `type` field in the payload. This cut total connections by ~6x.
- Strict separation of concerns. The WebSocket service only publishes/subscribes — no DB reads or writes. All persistence stays in the upstream services.
- Redis done properly. Used Redis Pub/Sub for fan-out, pipelining to batch commands, and Lua scripts where I needed atomic multi-step operations in a single round trip.
- Fix the timeout chain. Tuned timeouts at Cloudflare, Nginx, and the app layer, and added periodic ping/pong from the Gunicorn + Uvicorn layer so idle connections stay alive across every hop.
- Stay on the same EC2 (t2.small) to prove the gains came from the rewrite, not from throwing hardware at the problem. Deployed with Nginx + Gunicorn + Uvicorn workers (2 workers tuned for the instance size).
- Full observability stack — Prometheus for metrics, Loki for logs, Grafana for dashboards. Tracked active connections, handshake counts, disconnect reasons, per-client session duration, and error rates.

## Result

- Concurrent capacity went from ~500 (unstable) to ~3,000+ (stable) on the same t2.small instance.
- Connection drops and missed real-time updates were eliminated for the pilot's load profile.
- The service was rewritten, deployed, and stabilized within one month, solo.
- The pilot resumed successfully and management moved forward with the first production release.
- We now have real visibility into the service through Grafana, so future regressions are caught early instead of in production.

## What I Learned

- Observability is not optional — even a small amount of metrics and logging would have caught the original issues months earlier.
- Pick the right tool for the workload. Django is excellent for request/response and ORM-heavy work, but a pure fan-out WebSocket service benefits massively from an async-native framework.
- Understand the full network path. Many "WebSocket bugs" are actually proxy/timeout misconfigurations several layers above the application.
- Scope discipline matters under pressure. Keeping the service responsibility narrow (publish only, no DB) made the rewrite tractable inside a one-month window.

Looking back, the single biggest mistake from the previous team was not load testing the service properly before the pilot and pre-release testing. The service was built and shipped to the pilot stage purely on functional correctness, with no evidence it could hold up under realistic concurrent load. If even a basic load test had been run before the pilot, almost every issue I later had to fix — connection drops, memory saturation, the timeout chain — would have surfaced weeks earlier, in a much cheaper environment to fix them in.

If I were to do it again, I would push for load testing as a mandatory gate before any pilot or release, and add chaos testing around connection drops and Redis failover before going to production.
