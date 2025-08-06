import os
from google.cloud import bigquery
import json
from pydantic import BaseModel, Field

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
if not PROJECT_ID:
    raise RuntimeError("Environment variable GOOGLE_CLOUD_PROJECT is not set.")

def execute_query_tool(query: str) -> str:
    client = bigquery.Client(project=PROJECT_ID)
    try:
        query_job = client.query(query)
        results = query_job.result()
        rows = [dict(row) for row in results]
        return json.dumps(rows, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_table_schema(dataset_name):
    client = bigquery.Client(project=PROJECT_ID)
    dataset_ref = client.dataset(dataset_name)
    tables = client.list_tables(dataset_ref)
    schema_info = {}
    for table in tables:
        table_ref = dataset_ref.table(table.table_id)
        table_obj = client.get_table(table_ref)
        schema_info[table.table_id] = [field.name for field in table_obj.schema]
    return schema_info


class SubmitFinalAnswer(BaseModel):
    reasoning: str = Field(..., description="เหตุผลและกระบวนการคิด")
    sql: str = Field(..., description="SQL statement ที่ใช้")
    result: str = Field(..., description="ผลลัพธ์ตัวอย่าง")
    final_answer: str = Field(..., description="คำตอบสุดท้ายสำหรับผู้ใช้")