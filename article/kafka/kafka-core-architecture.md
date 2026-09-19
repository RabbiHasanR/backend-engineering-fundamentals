you can compare kafka with a container where only you can put items and can read one by one but can not modify or read specific item by thier position. so in formal way kafka is a distributed, replicated, append only log.


Producer: what is producer? producer is who produce any event or message and push to topic. producer can be any service who connect with kafka and push to topic

broker: what is broker? broker is a server or prcess where kafka topic partion live. when producer produce any event or message then this message produce to broker or topic or topic partion. so easy work we can say broker is a middle man who store event or message which produce from producer.

topic

partion

replication

consumer

consumer group