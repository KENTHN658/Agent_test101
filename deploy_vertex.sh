#!/bin/bash
set -e

# 1. CONFIGURATION (เติมค่าจริงให้เรียบร้อย)
PROJECT_ID="chromatic-timer-468017-m4"
REGION="us-central1"
REPO="agent-repo"
IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/agent:latest"

# รุ่นโมเดลล่าสุดที่ list มา (เลือก ID แถวบนสุด)
MODEL_RESOURCE="projects/205937060612/locations/${REGION}/models/8511366789614010368"

# Endpoint ที่สร้างมาแล้ว
ENDPOINT_RESOURCE="projects/205937060612/locations/${REGION}/endpoints/9222671647947882496"

DEPLOY_DISPLAY_NAME="creamadk-agent-deployment"
MACHINE_TYPE="n1-standard-2"

# 2. ตั้งค่า gcloud project
gcloud config set project "${PROJECT_ID}"

# 3. (ข้ามขั้นตอน build & upload เพราะคุณทำไว้แล้ว)

# 4. Deploy โมเดลลงใน Endpoint
gcloud ai endpoints deploy-model "${ENDPOINT_RESOURCE##*/}" \
  --region="${REGION}" \
  --model="${MODEL_RESOURCE}" \
  --display-name="${DEPLOY_DISPLAY_NAME}" \
  --machine-type="${MACHINE_TYPE}" \
  --traffic-split=0=100

echo "✅ Deployed model ${MODEL_RESOURCE##*/} to endpoint ${ENDPOINT_RESOURCE##*/}"

# 5. ทดสอบเรียกใช้งาน
echo "🔧 Testing predict ..."
curl -s -X POST \
  "https://${REGION}-aiplatform.googleapis.com/v1/${ENDPOINT_RESOURCE}:predict" \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -d '{
    "instances":[
      {"text":"สวัสดี Agent!"}
    ]
  }' | jq .

echo "🎉 Done!"
