#!/bin/bash

# Тестирование API эндпоинтов

BASE_URL="http://localhost:8000"

echo "Testing Gas Leak Detection API..."

# 1. Health check
echo -e "\n1. Health Check:"
curl -s ${BASE_URL}/health | jq '.'

# 2. Запуск обработки видео
echo -e "\n2. Start Batch Processing:"
curl -s -X POST ${BASE_URL}/api/v1/batch/process \
  -H "Content-Type: application/json" \
  -d '{
    "video_paths": [
      "/data/input_videos/test1.mp4",
      "/data/input_videos/test2.mp4"
    ]
  }' | jq '.'

# 3. Получение результатов
echo -e "\n3. Get Detections:"
curl -s "${BASE_URL}/api/v1/detections?limit=10" | jq '.'

echo -e "\nDone!"
