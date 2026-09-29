## What is Observability?

Observability refers to how easility we can understand what's happening inside a system, like an application or a service, by looking at the information it produces. Here a system is a distributed system which is combination of severel services or can be only single service. So in cloude the complexity of distributed systems, it can be challenging to understand what's happening inside each component or servercie at any given time. This is where observability becomes crucial.


So, to make distributed systems obserable, we use a model which has 3 factors:

1. What the system does? There is the workload. These are the operations a system does. Example, when a user sends a request, distributed system often breaks it down into smaller tasks handled by different services. this is also refered to as transaction.

2. How's the system built? There are software abstractions thats make up the structure of the distributed system. These elements are such as load balancer, services, pods, containers and more.

3.What it runs on? There are phisical machines tha provide computational components(RAM, CPU, disk space, network etc.)


However, before we can analyze any system, we must first capture of system behavior by a combination of logs, metrics and traces.


### Logs
A log is an append-only data structure that recors occuring in a system. A log consists of  text information of an any event in a system so looking at this information we can say what,when, how happen this event. 


### Metrics
Logs providing us detailed information about individual events. but if we want to see high level view like graph with stattistics, numerical value how our system change overtime. then metrics comes. metrics represent an aggregate.

### Traces
A distributed system can have severel services. so when any request comes from a user then this request often breaks it down into smaller tasks and each component responsible for their part of task. so at scale complex distributed system often we need to know how one request traveel through every components for trouble shooting or debugging. this is transaction tracing or distributed tracing.


These are the three pillers of Observability.

## What is Telemetry?
Telemetry is the process of automatically collecting logs, metrics and traces data and transmaittion data from remote or distributed systems to monitor, measure and track the performance or status of those system. Telemetry data provides real-time insights into how different parts of an application are performing, help developers and system administrators observe, troubleshoot, and optimize system without needing to manually check each component.


## Problems of traditional approch of Observability?

1. Logs, metrics, and traces live in separate silos
Each one is a different tool with different data. When something breaks, you jump from the metrics dashboard to the logging system to the tracing tool and try to connect the dots yourself. The real world doesn't have "logging problems" or "metrics problems". It just has problems, but the tools make you think in separate boxes. This puts a heavy mental load on the person on call.

2. Hard to find the full story of one request
Metrics tell you something happened at this time. Logs tell you what happened. But traditional logs often don't carry trace IDs or span IDs, so you can't easily follow one request across many services. The story of a single operation ends up scattered across many log lines with no clear thread.

3. No common standard, so data quality is poor
Every tool and library names things differently and formats data differently. Without a shared way to identify related events, correlating data across services is hard, and combining different logging libraries into one clear picture is even harder.

4. Open source libraries can't ship good telemetry
Most of your app is built from open source libraries, and their maintainers know best what to watch. But if a library adds one vendor's instrumentation, it forces that dependency on everyone. Tracing needs everyone to agree on one format to work at all. The workaround is "hooks and adapters", but then you must keep updating adapters with every new version, and converting between formats adds overhead.

5. Vendor lock-in
Instrumentation code is mixed into your app everywhere. If you want to switch tools later, you must rip out and rewrite all of it and migrate your dashboards too. That cost keeps teams stuck with the tool they started with.

6. Vendors also struggle
Building integrations for every library and framework is expensive and can't keep up with how fast software changes. So vendors spend their effort on converting data between formats instead of building better analysis tools. And converted data often loses quality, which makes it harder to analyze.

One-line summary: telemetry is disconnected, inconsistent, and tied to specific vendors, which makes finding the root cause of a problem slow and painful. This is the gap that a standard like OpenTelemetry tries to fill.

## What is OpenTelemetry?

OpenTelemetry (OTel) is an open source project designed to provied standarized tools and apis for generating, collecting and exporting telemetry data such as tracs, metrics and logs. It proiveds real observability view of the system to the developers and developers can easily find root cause of any issues. and develoepr can easily monitor, troubleshoot and optimize software systems.

Main goal of OPenTelemtry are:

1. combining traching, matrics and logs into a single framework and enabling correlationg of all telemetry data and establishing an open standard for telemetry data.

2. Integration with different backends for processing data easily

3. Supports various languages (java, python, go, etc.) and platforms, and making it versatile for different development environments.



## What OpenTelemetry is NOT

For better understanding of OpenTelemetry we must need to know what OpenTelemetry is Not.

1. OpenTelementry doesn't replace full-fledged monitoring or observability platform like datadog, new relic or prometheus. it  helps collect and standardize telemetry data so that we can send it to these tools for visualization and analysis.

2. OpenTelemetry doesn't store or visualize data. if only focus on the collection and export of telemetry data to external systems that handle storage and presentation, such as Grafana, Jeager or prometheus

3. OpenTelemetry is a toolkit for collecting and exporting telemetry data, but it requires configurations and integration with other systems. It dosen't automatically provide out of the box monitoring or alerting functionality.

4. While OpenTelemetry helps us collect details performance data, it doesn't automatically optimize application performance. It's diagnostic tool that helps us gather insights for manual tuning.

In essence, OpenTelemetry is an integration and standardization tool for telemetry data, not an all-in-one solution for monitoring, logging, or performance management. It complements other tools by standardizing the data collection process.