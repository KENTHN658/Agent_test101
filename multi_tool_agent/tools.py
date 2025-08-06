from google.cloud import bigquery
import json
from pydantic import BaseModel, Field

PROJECT_ID = "chromatic-timer-468017-m4"

def execute_query_tool(query: str) -> str:
    client = bigquery.Client(project=PROJECT_ID)
    try:
        query_job = client.query(query)
        results = query_job.result()
        rows = [dict(row) for row in results]
        return json.dumps(rows, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

class SubmitFinalAnswer(BaseModel):
    final_answer: str = Field(..., description="The final answer to submit to the user")
