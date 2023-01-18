# Spawn data infrastructure
```bash
make up

# checking redpanda console
make to_redpanda

# checking minio
make to_minio
```

# Prepare MySQL data source
```bash
make to_mysql

CREATE DATABASE brazillian_ecommerce;

USE brazillian_ecommerce;

CREATE TABLE olist_orders_dataset (
    order_id varchar(32),
    customer_id varchar(32),
    order_status varchar(16),
    order_purchase_timestamp varchar(32),
    order_approved_at varchar(32),
    order_delivered_carrier_date varchar(32),
    order_delivered_customer_date varchar(32),
    order_estimated_delivery_date varchar(32),
    PRIMARY KEY (order_id)
);

```

# Generation scripts
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/01_generate_orders.py
```