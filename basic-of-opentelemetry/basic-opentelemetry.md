# Why do we need opentelemetry?


## Current State of Observability

Observability = inferring internal system health from external outputs. Critical in distributed systems because complexity makes bugs hard to find.

The model has 3 factors: what the system does (workload/transactions), how it's built (software abstractions like containers and load balancers), and what it runs on (physical hardware resources). True troubleshooting requires looking at all three together — devs tend to focus on workload, ops tends to focus on hardware, but the real picture is the intersection. Real understanding = combine both perspectives.

Capturing system behavior is done through logs (what happened), metrics (how much/how fast), and traces (how a request traveled through services).

## Logs