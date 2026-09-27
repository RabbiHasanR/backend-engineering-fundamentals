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