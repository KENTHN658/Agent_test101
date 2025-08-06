from google.adk.agents import Agent
from .tools import execute_query_tool, SubmitFinalAnswer
from google.cloud import bigquery
import os

def get_schema_and_sample(project_id, sample_limit):
    client = bigquery.Client(project=project_id)
    output_lines = []
    datasets = list(client.list_datasets())
    if not datasets:
        return "No datasets found in this project."
    for dataset in datasets:
        dataset_id = dataset.dataset_id
        output_lines.append(f"\nDataset: {dataset_id}")
        tables = list(client.list_tables(dataset_id))
        if not tables:
            output_lines.append("  (No tables found)")
            continue
        for table in tables:
            table_id = table.table_id
            table_ref = f"{project_id}.{dataset_id}.{table_id}"
            table_obj = client.get_table(table_ref)
            columns = [f.name for f in table_obj.schema]
            column_str = ', '.join(columns)
            output_lines.append(f"  - {table_id}: {column_str}")

            # ดึง sample data
            try:
                query = f"SELECT * FROM `{table_ref}` LIMIT {sample_limit}"
                results = client.query(query).result()
                sample_rows = [dict(row) for row in results]
                if sample_rows:
                    # สรุปแค่ 2 แถวตัวอย่าง/หรือเฉพาะคีย์หลัก
                    sample_lines = []
                    for row in sample_rows:
                        row_str = ", ".join(f"{k}={v}" for k, v in row.items())
                        sample_lines.append(f"      {row_str}")
                    output_lines.append("    Sample rows:")
                    output_lines.extend(sample_lines)
                else:
                    output_lines.append("    (No sample data found)")
            except Exception as e:
                output_lines.append(f"    (Sample data error: {e})")
    return "\n".join(output_lines)


project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
get_schema_and_sample = get_schema_and_sample(project_id,5)

instruction = f"""
You are a professional data analyst using Google BigQuery.

Below is the current schema and sample data from project '{project_id}':
{get_schema_and_sample}

For each user question:
1. Identify the relevant tables and columns from the schema above (do not guess).
2. Write and execute the necessary BigQuery SQL using only the tables/columns above.
3. Summarize and reply in the same language as the user.
4. Do not show SQL code unless the user requests it.

If a question cannot be answered directly with the available data, politely explain why.
"""
#2. Write and execute the necessary BigQuery SQL using only the tables/columns above (do not show the SQL to the user).

instruction2 = f"""
You are a professional data analyst using Google BigQuery.

Below is the current schema and sample data from project '{project_id}':
{get_schema_and_sample}

For each user question:
1. Explain your thought process for selecting the relevant tables and columns (step by step, in the user's language).
2. Write and show the exact BigQuery SQL query you will execute.
3. Execute the SQL query (using execute_query_tool) and display the result (sample or summary if too large).
4. Based on the result, summarize the final answer clearly and concisely.
5. Return the final answer in this format (JSON):

{{
  "reasoning": "อธิบายว่าคุณเลือกตาราง/คอลัมน์ใดและเพราะอะไร",
  "sql": "โชว์ SQL ที่คุณจะรัน",
  "result": "แสดงตัวอย่างหรือผลลัพธ์ที่ได้",
  "final_answer": "คำตอบสุดท้ายสำหรับผู้ใช้"
}}

If a question cannot be answered directly, explain why.

**Respond in the same language as the user.**
"""

root_agent = Agent(
    name="bigquery_data_agent",
    model="gemini-2.0-flash",
    instruction=instruction2,
    tools=[execute_query_tool, SubmitFinalAnswer],
)
