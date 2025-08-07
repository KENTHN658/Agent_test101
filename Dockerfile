FROM python:3.13-slim
WORKDIR /app

# ติดตั้ง dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# คัดลอกโค้ดและคีย์ service account
COPY . .

# กำหนด env ใน container ให้ตรงกับโค้ด
ENV GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/config.json

# เปิดพอร์ตให้ Vertex AI เรียก /predict ได้
EXPOSE 8080

# รันเป็น FastAPI app (ติดตั้ง fastapi ใน requirements.txt :contentReference[oaicite:1]{index=1})
CMD ["uvicorn", "multi_tool_agent.agent:app", "--host", "0.0.0.0", "--port", "8080"]
