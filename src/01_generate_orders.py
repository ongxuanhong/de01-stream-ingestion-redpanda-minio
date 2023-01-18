import contextlib
from time import sleep

import pandas as pd
from sqlalchemy import create_engine


class MysqlLoader:
    def __init__(self, params):
        self.params = params

    @contextlib.contextmanager
    def get_db_connection(self):
        conn_info = (
                f"mysql+pymysql://{self.params['user']}:{self.params['password']}"
                + f"@{self.params['host']}:{self.params['port']}"
                + f"/{self.params['database']}"
        )
        db_conn = create_engine(conn_info).connect()
        try:
            yield db_conn
        except Exception:
            raise
        finally:
            db_conn.close()

    def extract_data(self, sql: str) -> pd.DataFrame:
        with self.get_db_connection() as db_conn:
            pd_data = pd.read_sql(sql, db_conn)
            return pd_data


# load sample data
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

# setup MySQL connection
mysql_db_params = {
    "host": "mysql",
    "port": "3306",
    "database": "brazillian_ecommerce",
    "user": "root",
    "password": "debezium",
}
db_loader = MysqlLoader(mysql_db_params)

# generating data
ls_daily = sorted(pd_orders["daily"].unique().tolist())
print("NO. DATES:", len(ls_daily))
tbl_name = "olist_orders_dataset"
ls_columns = db_loader.extract_data(f"SELECT * FROM {tbl_name} LIMIT 1;").columns

n_days = 3
for i, daily in enumerate(ls_daily):
    if i < n_days:
        print("Writing data on:", daily)
        pd_load = pd_orders.query(f"daily == '{daily}'")
        print("-Records:", len(pd_load))

        # insert new records
        with db_loader.get_db_connection() as db_conn:
            try:
                # insert new data
                pd_load[ls_columns].to_sql(
                    tbl_name,
                    db_conn,
                    if_exists="append",
                    index=False,
                    chunksize=10000,
                    method="multi",
                )
            except Exception as err:
                print(f"Error: {str(err)[:500]}...{str(err)[-500:]}")

        sleep(5)
