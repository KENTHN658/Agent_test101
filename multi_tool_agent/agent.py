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
1. Identify and use the relevant tables and columns from the schema above (do not guess).
2. Directly write and execute the necessary BigQuery SQL using only the tables/columns above.
3. Summarize and reply with the analysis result in the same language as the user, without explaining your steps or which tables/columns you used.
4. Do not show SQL code unless the user requests it.

If a question cannot be answered directly with the available data, politely explain why.
**Always respond in the same language as the user.**
"""


#2. Write and execute the necessary BigQuery SQL using only the tables/columns above (do not show the SQL to the user).
root_agent = Agent(
    name="bigquery_data_agent",
    model="gemini-2.0-flash",
    instruction=instruction,
    tools=[execute_query_tool, SubmitFinalAnswer],
)
