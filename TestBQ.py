import vertexai
from vertexai import agent_engines

vertexai.init(
    project="chromatic-timer-468017-m4",               # Your project ID.
    location="us-central1",                # Your cloud region.
    staging_bucket="gs://test bucket",
)
