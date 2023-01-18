import json
import random
from datetime import datetime
from time import sleep

import pandas as pd
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic

# Create kafka topics if running in Docker.
BOOTSTRAP_SERVERS = "localhost:9092"
admin_client = KafkaAdminClient(bootstrap_servers=BOOTSTRAP_SERVERS)

# Check if topic already exists first
event_name = "clickstream_events"
existing_topics = admin_client.list_topics()
if event_name not in existing_topics:
    print("Create topic:", event_name)
    admin_client.create_topics(
        [NewTopic(event_name, num_partitions=1, replication_factor=1)]
    )

load_dtypes = {
    "order_id": "str",
    "customer_id": "str",
    "order_status": "str",
    "order_purchase_timestamp": "str",
    "order_approved_at": "str",
    "order_delivered_carrier_date": "str",
    "order_delivered_customer_date": "str",
    "order_estimated_delivery_date": "str",
}

pd_orders = pd.read_csv("data/olist_orders_dataset.csv", dtype=load_dtypes)
print(pd_orders.shape)

# loop through each day
ls_daily = sorted(pd_orders["daily"].unique().tolist())
print("NO. DATES:", len(ls_daily))

# Create a Kafka producer to interact with Redpanda
producer = KafkaProducer(bootstrap_servers=BOOTSTRAP_SERVERS)

n_days = 3
for i, daily in enumerate(ls_daily):
    if i < n_days:
        print("Getting clickstream data on:", daily)
        pd_load = pd_orders.query(f"daily == '{daily}'")
        ls_customers = pd_load["customer_id"].unique()
        print("-Number of customers:", len(ls_customers))

        for key in ls_customers:
            # Generate randomized user event data for a non-existing website
            data = {
                "timestamp": datetime.now().isoformat(),  # ISO 8601 timestamp, because Trino can only parse this
                "event_name": random.choice([
                    "email_click",
                    "link_1_click",
                    "link_2_click",
                    "pdf_download",
                    "video_play",
                    "website_visit",
                ]),
                "event_value": random.randint(0, 1),
            }

            # Send the data to the Redpanda topic
            key = key.encode("utf-8")
            value = json.dumps(data).encode("utf-8")
            producer.send(event_name, key=key, value=value)

        print(
            f"Sent data to Redpanda topic {event_name}: {key} - {value}, sleeping for 1 second"
        )

        sleep(1)
