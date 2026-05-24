# Walk Me Through Your Current Project

## One-line Summary

I work at a sports-tech company building a real-time scoring and streaming platform for sports like cricket, football, and baseball. The product shows live scores, match info, notifications, and a video stream to thousands of concurrent users, and my work sits on the backend services that power that real-time experience.

## Product Context

A scorer inputs live scores from the ground. Every connected user — on web and mobile — must see score updates, match events, notifications, and other live data instantly, while a live video stream plays alongside the scoreboard. Latency, reliability, and concurrency are the core quality bars of the product, because if real-time breaks, the product breaks.

## Architecture (High Level)

The platform is a set of Python microservices communicating over HTTP and Redis, fronted by Cloudflare and Nginx, and deployed on AWS EC2 with Docker.

Main components I work with:

- **Core API service** — FastAPI + PostgreSQL. Handles match creation, teams, players, fixtures, user accounts, and all CRUD for scoring data. This is the source of truth.
- **Scoring service** — Receives scorer input, validates it, persists it, and publishes events for downstream consumers.
- **WebSocket fan-out service** — FastAPI, async, Redis Pub/Sub. Pure fan-out: no DB reads or writes. Pushes score updates, notifications, and live events to all connected clients in real time.
- **Notification service** — Handles push notifications and in-app alerts.
- **Streaming layer** — Live video stream synced with the scoreboard.
- **Observability stack** — Prometheus, Loki, Grafana for metrics, logs, and dashboards across all services.

## My Role

I'm a backend engineer, primarily in Python (FastAPI and Django). My responsibilities cover:

- Designing and building backend services and APIs.
- Owning the real-time WebSocket service end-to-end — design, implementation, deployment, and observability.
- Database design and query tuning on PostgreSQL (including stored procedures / PL/pgSQL where it makes sense).
- Redis usage patterns — Pub/Sub for fan-out, pipelining for batching, Lua scripts for atomic multi-step operations.
- CI/CD and deployment on AWS EC2 with Docker, behind Nginx and Cloudflare.
- Observability — wiring services into Prometheus, Loki, and Grafana, and building dashboards for active connections, latency, and error rates.

## A Concrete Piece of Work

The clearest example of what I do is the WebSocket rewrite. The legacy service (Django + Django Channels + Redis) couldn't reliably hold even 300–500 concurrent users, connections were dropping, and we had no observability. I was assigned to fix it solo with a one-month deadline before the first production release.

I rewrote it in FastAPI as a pure async fan-out service:

- Collapsed 6–7 routes per user into a single multiplexed connection dispatched by a `type` field — cut total connections by ~6x.
- Removed all DB work from the service; it only does Redis Pub/Sub fan-out now.
- Fixed the timeout chain across Cloudflare, Nginx, and the app, plus periodic ping/pong to keep idle connections alive.
- Added Prometheus + Loki + Grafana with dashboards for active connections, handshake counts, disconnect reasons, and error rates.

On the same EC2 t2.small instance, concurrent capacity went from ~500 unstable to 3,000+ stable, and the pilot resumed successfully.

## Tech Stack I Use Day-to-Day

- **Languages:** Python (primary), JavaScript, Bash.
- **Backend:** FastAPI, Django, Django REST Framework.
- **Databases:** PostgreSQL (with PL/pgSQL functions and procedures where useful), Redis, MongoDB.
- **Infra:** Docker, docker-compose, AWS (EC2, S3, RDS, CloudWatch), Nginx, Cloudflare.
- **Observability:** Prometheus, Loki, Grafana, OpenTelemetry.
- **CI/CD:** GitHub Actions.

## What I Enjoy About It

Two things. First, the workload is genuinely hard — real-time, high-concurrency, latency-sensitive — so engineering decisions actually matter and show up in user experience immediately. Second, I get to own services end-to-end: design, implementation, deployment, and observability, instead of just shipping features into someone else's system.

## What I'd Improve Next

- Load testing as a mandatory gate before any release, with realistic concurrency profiles.
- Chaos testing around Redis failover and connection drops.
- Moving from a single EC2 host toward an autoscaled setup behind a proper LB once traffic justifies it.
- Tighter SLOs on real-time latency and connection stability, tracked in Grafana with alerting.





