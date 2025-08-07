# Dockerfile

FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --root-user-action=ignore -r requirements.txt

COPY . .

# ให้ container รู้จัก PORT ที่ระบบจะตั้งให้
ENV PORT 8080
EXPOSE 8080

# รันด้วย sh -c เพื่อให้ $PORT ถูกแทนค่าจริงตอน start
CMD ["sh", "-c", "uvicorn multi_tool_agent.agent:app --host 0.0.0.0 --port $PORT"]
