schema registry:

server process external to kafka brokers

maintains a database of schemas

HA deployment option available

consumer/producer api component

defines schema compatibility rules per topic

producer api prevents incompatible messages from being produced

consumer api prevents incompatible messages from being consumed


supported formats

json schema

avro

protocol buffers

