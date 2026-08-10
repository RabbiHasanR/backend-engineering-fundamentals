Topics: 

. named container for similar events. systems contain lots of topics. can duplicate data between topics

. durable logs of events. append only. can only seek by offset, not indexed

. events are immutable

topics are durable

retention period is configurable.

logs soted in disk



kafka topic - organizing your data streams

message categorization: topics group related messages logically

immutable log: messages in a topic are stored sequentially

multi consumer access: multiple consumers can read from the same topic

decoupled communication: producers and consumers interact through topics, not directly

replication: topics ensure data availability with replication across brokers

