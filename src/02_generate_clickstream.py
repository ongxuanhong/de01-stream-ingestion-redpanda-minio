import json
import random
from datetime import datetime
from time import sleep

import pandas as pd
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic

# Create kafka topics
BOOTSTRAP_SERVERS = "redpanda:9092"

EVENTS_TOPIC_NAME = "clickstream_events"

MOCK_EVENTS = [
    "email_click",
    "link_1_click",
    "link_2_click",
    "pdf_download",
    "video_play",
    "website_visit",
]

admin_client = KafkaAdminClient(bootstrap_servers=BOOTSTRAP_SERVERS, client_id="user-event-producer")

# Check if topic already exists first
existing_topics = admin_client.list_topics()
if EVENTS_TOPIC_NAME not in existing_topics:
    print("Create topic:", EVENTS_TOPIC_NAME)
    admin_client.create_topics(
        [NewTopic(EVENTS_TOPIC_NAME, num_partitions=1, replication_factor=1)]
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

        for j, cust in enumerate(ls_customers):
            # Generate randomized user event data for a non-existing website
            data = {
                "timestamp": datetime.now().isoformat(),
                "daily": daily,
                "EVENTS_TOPIC_NAME": random.choice(MOCK_EVENTS),
                "event_value": random.randint(0, 1),
            }

            # Send the data to the Redpanda topic
            key = cust.encode("utf-8")
            value = json.dumps(data).encode("utf-8")
            producer.send(EVENTS_TOPIC_NAME, key=key, value=value)

            print(
                f"{i}.{j}. Sent data to Redpanda topic {EVENTS_TOPIC_NAME}: {key} - {value}, sleeping for 3 second"
            )

        sleep(3)
