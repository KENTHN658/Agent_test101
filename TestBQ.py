from google.cloud import bigquery
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/thn_ken/keys/my-service-account-cream.json"

client = bigquery.Client()

query = """
SELECT COUNT(DISTINCT customer_unique_id) AS total_customers
FROM `chromatic-timer-468017-m4.ECOM.olist_customers_dataset`
"""

query_job = client.query(query)
results = query_job.result()

for row in results:
    print(f"Total customers: {row.total_customers}")