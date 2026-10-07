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



## OpenTelemetry Framework

### OpenTelemetry Signals & Specification: Quick Recall Notes

Big picture

OTel is organized into signals: tracing, metrics, logging.
Each signal is a standalone component, but data streams can be linked (e.g., trace IDs in logs).
Everything is defined in a language-agnostic specification, the core of the project. It keeps all language implementations consistent and interoperable. End users rarely touch it directly.

The spec has 3 parts

Glossary: shared vocabulary so everyone means the same thing by a term.
Signal design, split into two layers per signal:
API: conceptual interfaces implementations must follow. It defines how to generate, process, and export telemetry, and keeps implementations compatible.
SDK: the guide for language implementers. It sets the requirements a language-specific implementation must meet, covering configuration, processing, and exporting.
Telemetry data rules:
Semantic conventions: consistent naming and meaning for common metadata, so you don't have to normalize data from different sources.
OTLP (OpenTelemetry Protocol): the standard wire protocol for sending telemetry (covered later in the chapter).

Memory hook

Signals (traces, metrics, logs) → defined in the Spec → = Glossary + API/SDK + Semantic Conventions + OTLP

API = what you call. SDK = how it's implemented.
Semconv = consistent names. OTLP = consistent transport.


### Vendor-Agnostic, Language-Specific Instrumentation

**What is this about?**
It explains how OpenTelemetry is built in each programming language (Python, Java, etc.), and *why* it is split into two parts: **API** and **SDK**.

**The two parts**

* **API** = the "buttons" you press in your code, like `start_span()` or `counter.add()`. It only defines *what you can call*. It does nothing by itself.
* **SDK** = the "engine" behind the buttons. It does the real work: creates, processes, and sends telemetry. The official SDK is the reference one, but you can write your own.

**How it works**

1. Your app starts and **registers a provider** for each signal (trace, metric, log). The provider is the SDK.
2. When code calls the API, the call is forwarded to that provider.
3. If you did **not** register any provider, a fallback provider is used, which does **nothing** (**no-op**). No error, no cost.

**Ways to add instrumentation (all use the API)**

* **Zero-code / automatic**: no code changes.
* **Instrumentation libraries**: simple integration, small or no code changes.
* **Manual**: you write the code yourself, for full control.

**Why split API and SDK? (the main point)**
Imagine you build an open source library, like a database driver, and you want to add observability to it.

* The **API is small and safe**. Any library can depend on it without causing trouble.
* The **SDK is big and complex**, with many dependencies. If libraries forced it on everyone, it could **conflict** with the user's own packages.

So the split gives you three benefits:

1. **Libraries can ship with built-in instrumentation** easily (they only depend on the light API).
2. **The app owner chooses the SDK**, so they can fix dependency conflicts or use a different implementation.
3. **No cost if unused**: if the user does not want telemetry, the no-op provider runs and adds almost no overhead.

**Code example**

SDK (once, at app startup):

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

provider = TracerProvider()                                  # SDK = the engine
provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4317"))
)
trace.set_tracer_provider(provider)                          # register the provider
```

API (anywhere in your code):

```python
from opentelemetry import trace                              # API = the buttons

tracer = trace.get_tracer(__name__)

def create_order(order_id):
    with tracer.start_as_current_span("create-order") as span:
        span.set_attribute("order.id", order_id)
```

If the SDK block is never run, `create_order` still works and tracing is a no-op.

**Easy memory trick**
**API** = the plug socket on the wall (same everywhere, light, safe).
**SDK** = the electricity supply (heavy, your choice, you connect it).
No supply connected? The socket just does nothing.

**One line to remember:**
*Libraries use the light API. Apps choose the SDK. No SDK means no-op.*








### Telemetry Processor (Standalone Component)

**What is this about?**
Instrumentation (API + SDK) only *creates and emits* telemetry. After that, someone must **manage the data and deliver it to backends**. This is the operator's job, and OpenTelemetry gives a standalone tool for it: the **OpenTelemetry Collector** (similar in idea to Fluent Bit).

**The full flow**

```
Sources → Collector (receive → process → export) → Backends → Analysis
```

**1. Collect (Receivers)**
Gather data from many sources: apps using the OTel SDK (via OTLP), Prometheus metrics, log files, other agents.

**2. Process (Processors)**
The Collector cleans and prepares the data:
- **Parse / convert** into a common format
- **Enrich** with extra metadata (service name, environment, host)
- **Filter** out useless data to cut noise and storage cost
- **Normalize / transform** the data
- **Buffer** for resilience and performance (no data loss if a backend is slow or down)

**3. Transmit (Exporters)**
- **Route** different data to different places
- **Forward** to one or many backends

**4. Analyze (Backends)**
Backends store and show the data, for example: Jaeger or Tempo (traces), Prometheus (metrics), Loki (logs), Grafana (dashboards).

**Easy memory trick**

> **Collector = a post office.**
> It **receives** letters from many senders, **sorts and stamps** them (process), then **delivers** them to the right addresses (backends).

**One line to remember:**
*Receivers collect → Processors clean → Exporters deliver to backends → Backends let you analyze.*





### Wire Protocol (OTLP)

**What is this about?**
After telemetry is created (SDK) and managed (Collector), it must travel across the network: from apps to the Collector to backends. OpenTelemetry defines one standard for this: **OTLP (OpenTelemetry Protocol)**.

**What OTLP defines**
- **Encoding**: how data is represented (the format)
- **Transport**: how data is sent over the network

It is **open source and vendor-neutral**, so it works across the whole observability stack.

**Why OTLP is preferred**
- The **Collector uses OTLP internally**, so sending OTLP means **no format conversion**, which saves cost and keeps data consistent.
- The format matches OTel ideas: attributes follow **semantic conventions**, and signals can be **correlated** (trace ↔ logs ↔ metrics).
- The Collector can also receive and export other formats (Prometheus, Zipkin), but OTLP is the best choice.

**Why it is good for the ecosystem**
- **Most backends support OTLP out of the box.**
- Tool developers no longer build many adapters for many proprietary formats.
- Result: **better interoperability** between tools.

**Transport options (3)**
- HTTP/1.1
- HTTP/2
- gRPC

Choose based on performance, reliability, and security needs.

**Encoding options (2)**

| Format | Good | Bad |
|---|---|---|
| **Protobuf** (binary, common default) | Compact, fast, supports schema changes without breaking compatibility | Not human-readable |
| **JSON** | Human-readable | Bigger size, more network traffic |

**Easy memory trick**

> **OTLP = a universal shipping container.**
> Any app can pack data in it, any backend can open it, so nobody needs special adapters.

**One line to remember:**
*OTLP is the one standard language (Protobuf or JSON, over HTTP or gRPC) that every OTel component and most backends understand.*




## Instrumentation

Instrumentation refers to the process of adding code or using tools to collect telemetry data (such as logs, metrics, and traces) from an application.

Basically instrumentation is adding someting in application code for collect telemetry data to make any non observed application into an observable application.

However, instrumentation is often highly dependent on the programming language and framework in use. This means that instrumentation code tends to be proprietary, tailored to the specific tools, libraries and achitecture of each application. As a result developers mustt often implement custom instrumentation for each language or framework they work with, which can lead to challenges in maintaining consistency across different parts of a system, expecially in polyglot(multi language) environments.

It also means that the more specific the information you want to extract from your application, the more specific your instrumentation effort has to be.

The instrumentation also defines which kind of telemetry signals are being handled.

### Categories for OpenTelemetry Instrumentation

a. Automatic instrumentation(zero code): No code change require, low effort, limited control, minimal customization

b. Instrumentation Libraries: Can be need minimal or moderate code change require, Moderate effort, medium control(some configuration), Moderate framework level customization.

c. Manual Instrumentation: Requires explicit code changes. this involves directly adding OpenTelemetry API calls in the source code. high effort, full control, full customization.


## Opentelemetry Collector