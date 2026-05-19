# Biggest Technical Challenge I Faced



The biggest technical challenge I've faced recently was rewriting a failing production WebSocket service, solo, in one month, while our company's first release was on the line.

 

I work at a sports-tech company that runs a real-time scoring platform for cricket, football, and baseball. Live score updates, notifications, and stream sync are the core product — if real-time breaks, the product breaks.


During our pilot, the existing WebSocket service — built on Django, Django Channels, and Redis — couldn't reliably hold even 300 to 500 concurrent users. Connections were dropping constantly, and we had zero observability, so nobody could explain why.

The original developers were gone, the rest of the team was committed to other services, and management had already planned the release right after the pilot. The pilot had to be paused, which made it very visible. I was assigned to fix it alone, with a one-month deadline.



I mapped the system end-to-end and found four main issues:

1. Each user opened 6–7 separate WebSocket routes, so 500 users meant about 3,500 live connections.
2. The WebSocket consumers were doing DB reads and writes, which they shouldn't — this service should only fan out messages.
3. Django plus Django Channels was memory-heavy and sync-first, the wrong fit for a high-connection, low-CPU workload.
4. The full path — Cloudflare, Nginx, Daphne — had HTTP-style timeouts that were silently killing long-lived WebSocket connections.

On top of that, there was no monitoring at all, so debugging was guesswork.



I decided to rewrite the service instead of patching it. Four key choices:

- I chose FastAPI because it's async-native, low-memory, and I had already shipped several production services on it — so I could move fast under the deadline.
- I collapsed the 6–7 routes per user into a single multiplexed connection, dispatched by a `type` field. That alone cut total connections by about 6x.
- I removed all DB work from the service. It now only does Redis pub/sub fan-out.
- I added a proper observability stack — Prometheus, Loki, and Grafana — so we'd never be blind again.

I also fixed the timeout chain across Cloudflare, Nginx, and the app layer, and added periodic ping/pong to keep idle connections alive.



On the exact same EC2 t2.small instance, concurrent capacity went from around 500 unstable connections to over 3,000 stable ones. The pilot resumed, the release moved forward, and the whole rewrite shipped in one month.


The biggest takeaway — and honestly the previous team's biggest mistake — was that the service was never load-tested before the pilot. If even a basic load test had been run earlier, almost every issue I had to fix would have surfaced weeks before, in a far cheaper environment. Since then, I treat load testing as a mandatory gate, not an afterthought.
