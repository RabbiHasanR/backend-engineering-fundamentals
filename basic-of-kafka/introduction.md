apache kafka event streaming platform which is used to collect, store and process real time data streams at scale.

it has numerous use cases, including distributed logging, stream processing and pub sub masseging.




Event: an event is just a thing that has happened. like internet of things, bussiness process change, user interaction, microservice outpu

an event in kafka is modeled as a key value pair.  internally, inside kafka when these things are actually store, keys and values ar just sequence of bytes. kafka is internally loosely typed.

 key can be complex domain objects, but are often just primitive types like strings or integers.



