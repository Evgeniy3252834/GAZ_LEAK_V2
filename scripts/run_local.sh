#!/bin/bash

# Скрипт для локального запуска всех сервисов

echo "Starting Gas Leak Detection System..."

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Please install Docker first."
    exit 1
fi

# Проверка наличия docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "docker-compose not found. Please install docker-compose first."
    exit 1
fi

# Создание необходимых директорий
mkdir -p data/{input_videos,processed,results}
mkdir -p logs
mkdir -p models

# Запуск сервисов
cd docker
docker-compose -f docker-compose.full.yml up -d

echo "Services started:"
echo "  - API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Airflow: http://localhost:8080"
echo "  - Health: http://localhost/health"

echo ""
echo "Useful commands:"
echo "  - View logs: docker-compose -f docker/docker-compose.full.yml logs -f"
echo "  - Stop services: docker-compose -f docker/docker-compose.full.yml down"
echo "  - Restart: docker-compose -f docker/docker-compose.full.yml restart"

# Показать статус
docker-compose -f docker-compose.full.yml ps
