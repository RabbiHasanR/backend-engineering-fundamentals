brokers: 

an computer, instance, or container running the kafka process
manages partitions
handle write and read requests
manage replication of partitions
intentionally very simple





kafka broker - the foundation of message storage

message management: brokers handle storing, retriving, and distributing messages

cluster node: each broker is a node in the kafka cluster

scalability: brokers enable horizontal scaling by distributing data across nodes

fault tolerance: redundancy ensures message durability during broker failures

dynamic membership: brokers can join or leave clusters without downtime

