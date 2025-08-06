from google.cloud import bigquery

def get_schema_and_sample(project_id, sample_limit=5):
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

# ตัวอย่างการใช้งาน
project_id = "chromatic-timer-468017-m4"
schema_and_sample_text = get_schema_and_sample(project_id, sample_limit=2)
print(schema_and_sample_text)