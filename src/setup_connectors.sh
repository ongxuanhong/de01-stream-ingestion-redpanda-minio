# create src-brazillian-ecommerce connector
curl --request POST \
  --url http://localhost:8083/connectors \
  --header 'Content-Type: application/json' \
  --data '{
  "name": "src-brazillian-ecommerce",
  "config": {
    "connector.class": "io.debezium.connector.mysql.MySqlConnector",
    "tasks.max": "1",
    "database.hostname": "mysql",
    "database.port": "3306",
    "database.user": "debezium",
    "database.password": "dbz",
    "database.server.id": "184054",
    "database.include.list": "brazillian_ecommerce",
    "topic.prefix": "dbserver1",
    "schema.history.internal.kafka.bootstrap.servers": "redpanda:9092",
    "schema.history.internal.kafka.topic": "schema-changes.brazillian_ecommerce"
  }
}'

# create connector S3
curl --request POST \
  --url http://localhost:8083/connectors \
  --header 'Content-Type: application/json' \
  --data '{
  "name": "sink-s3-brazillian-ecommerce",
  "config": {
    "topics.regex": "dbserver1.brazillian_ecommerce.*",
    "topics.dir": "brazillian_ecommerce",
    "connector.class": "io.confluent.connect.s3.S3SinkConnector",
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "format.class": "io.confluent.connect.s3.format.json.JsonFormat",
    "flush.size": "100",
    "store.url": "http://minio:9000",
    "storage.class": "io.confluent.connect.s3.storage.S3Storage",
    "s3.region": "us-east-1",
    "s3.bucket.name": "warehouse",
    "aws.access.key.id": "minio",
    "aws.secret.access.key": "minio123"
  }
}'