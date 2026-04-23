
[![Coverage](https://img.shields.io/badge/coverage-73%25-brightgreen.svg)](https://github.com/Evgeniy3252834/GAZ_LEAK_V2)



markdown
# Gas Leak Detection System

[![Coverage](https://img.shields.io/badge/coverage-73%25-brightgreen.svg)](https://github.com/Evgeniy3252834/GAZ_LEAK_V2)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red.svg)](https://pytorch.org/)
[![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)](https://www.docker.com/)
[![Airflow](https://img.shields.io/badge/Airflow-2.5+-orange.svg)](https://airflow.apache.org/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

**Система детекции утечек газа с помощью дронов** — использует компьютерное зрение для анализа тепловизионных изображений и автоматического обнаружения шлейфа газа.

---

## 📋 Оглавление

- [Описание проекта](#описание-проекта)
- [Архитектура](#архитектура)
- [Технологии](#технологии)
- [Сущности предметной области](#сущности-предметной-области)
- [Внешние системы](#внешние-системы)
- [Батчевый сервис](#батчевый-сервис)
- [Пошаговая установка](#пошаговая-установка)
- [Запуск](#запуск)
- [API Эндпоинты](#api-эндпоинты)
- [Тестирование](#тестирование)
- [Docker](#docker)
- [Airflow DAG](#airflow-dag)
- [Идемпотентность и Бэкфилл](#идемпотентность-и-бэкфилл)
- [Переменные окружения](#переменные-окружения)
- [Структура проекта](#структура-проекта)
- [Устранение неполадок](#устранение-неполадок)
- [Лицензия](#лицензия)

---

## Описание проекта

Система анализирует видео с тепловизора и RGB-камеры, определяет наличие шлейфа газа и при обнаружении отправляет дрон для подтверждения газоанализатором.

### Основные возможности

| Возможность | Описание |
|-------------|----------|
| 🔍 **Детекция утечек** | Анализ тепловизионных изображений через нейросеть (ResNet18) |
| 📹 **Обработка видео** | Извлечение кадров и пакетная обработка |
| 🚀 **API сервер** | REST API для интеграции с дронами (FastAPI) |
| ⚡ **Асинхронная обработка** | Фоновые воркеры для длительных задач |
| 📊 **Оркестрация** | Airflow DAG с DockerOperator |
| 🐳 **Docker контейнеризация** | Простое развертывание |
| 🔒 **Идемпотентность** | Защита от повторной обработки видео |
| 📦 **Батчевая обработка** | Массовая обработка видеофайлов |

---

## Архитектура

Проект построен на **Clean Architecture** (Чистая архитектура) с разделением на независимые слои:
┌─────────────────────────────────────────────────────────────────────┐
│ ВНЕШНИЙ МИР │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│ │ Дрон │ │Тепловизор│ │RGB камера│ │Газоанализатор│ │
│ └────┬────┘ └────┬────┘ └────┬────┘ └──────┬──────┘ │
│ └────────────┴────────────┴──────────────┘ │
│ │ │
│ ▼ │
│ ┌───────────────────────────────────────────────────────────────┐ │
│ │ API Gateway (Nginx) │ │
│ └───────────────────────────────────────────────────────────────┘ │
│ │ │
│ ┌───────────────────────────┼───────────────────────────────────┐ │
│ │ ▼ │ │
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │ │
│ │ │API (FastAPI)│ │ Worker 1 │ │ Worker N │ │ │
│ │ │ Port 8000 │ │ (фоновый) │ │ (фоновый) │ │ │
│ │ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ │ │
│ │ │ │ │ │ │
│ │ └────────────────┼────────────────┘ │ │
│ │ ▼ │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ USE CASES │ │ │
│ │ │ • DetectLeakUseCase │ │ │
│ │ │ • BatchProcessUseCase │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ │ │ │ │
│ │ ┌─────────────────────────────────────────────────────┐ │ │
│ │ │ DOMAIN (Entities) │ │ │
│ │ │ • LeakDetectionResult │ │ │
│ │ │ • VideoFrame │ │ │
│ │ │ • BatchJob │ │ │
│ │ │ • LeakConfirmation │ │ │
│ │ └─────────────────────────────────────────────────────┘ │ │
│ │ │ │ │
│ │ ┌───────────┐ ┌───────────┐ ┌───────────┐ │ │
│ │ │ Model │ │ Video │ │ Repository│ │ │
│ │ │ Inference │ │ Processor │ │ (SQLite/ │ │ │
│ │ │ (PyTorch) │ │ (OpenCV) │ │ Postgres) │ │ │
│ │ └───────────┘ └───────────┘ └───────────┘ │ │
│ └────────────────────────────────────────────────────────────────┘ │
│ │
│ ┌─────────────────────────────────────────────────────────────────┐│
│ │ ORCHESTRATION (Airflow) ││
│ │ • check_for_new_videos → backfill → process_videos_batch ││
│ └─────────────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────────────┘

text

### Слои архитектуры

| Слой | Назначение | Файлы |
|------|------------|-------|
| **Domain** | Бизнес-сущности и интерфейсы | `src/domain/` |
| **Use Cases** | Бизнес-логика | `src/usecases/` |
| **Infrastructure** | Реализация интерфейсов (БД, модель, видео) | `src/infrastructure/` |
| **API** | REST эндпоинты | `src/api/` |
| **CLI** | Командная строка | `src/cli/` |

---

## Технологии

| Компонент | Технология | Версия |
|-----------|------------|--------|
| **Язык** | Python | 3.9+ |
| **API фреймворк** | FastAPI | 0.100+ |
| **ML фреймворк** | PyTorch | 2.0+ |
| **Векторные вычисления** | NumPy | 1.24+ |
| **Работа с изображениями** | Pillow, OpenCV | 10.0+, 4.8+ |
| **База данных** | SQLite / PostgreSQL | - |
| **Кэширование** | Redis | 6+ |
| **Оркестрация** | Apache Airflow | 2.5+ |
| **Контейнеризация** | Docker, Docker Compose | - |
| **Web сервер** | Nginx | Alpine |
| **Тестирование** | pytest, pytest-cov | 7.4+, 4.1+ |

---

## Сущности предметной области

### 1. `LeakDetectionResult` - Результат детекции утечки

```python
@dataclass
class LeakDetectionResult:
    frame_id: str              # ID кадра
    timestamp: datetime        # Время детекции
    leak_probability: float    # Вероятность утечки (0-1)
    is_leak: bool              # Есть ли утечка
    confidence: float          # Уверенность модели
    video_path: str            # Путь к видео
    bounding_box: Optional[tuple]  # Координаты шлейфа
### 2. `VideoFrame` - Видеофрейм для анализа

```python
@dataclass
class VideoFrame:
    timestamp: datetime        # Время кадра
    thermal_image: bytes       # Тепловизионное изображение
    rgb_image: Optional[bytes] # RGB изображение (опционально)
    frame_index: int           # Номер кадра
    video_path: str            # Путь к видео
### 3. `BatchJob` - Батчевая задача

```python
@dataclass
class BatchJob:
    job_id: str                # Уникальный ID задачи
    video_paths: List[str]     # Список видео для обработки
    status: ProcessingStatus   # Статус обработки
    created_at: datetime       # Время создания
    updated_at: datetime       # Время обновления
    results: List[LeakDetectionResult]  # Результаты
    error_message: Optional[str]        # Сообщение об ошибке
### 4. `LeakConfirmation` - Подтверждение утечки

```python
@dataclass
class LeakConfirmation:
    leak_id: str
    detection_result: LeakDetectionResult
    confirmed: bool
    gas_concentration: Optional[float]
    confirmed_at: datetime
    status: LeakStatus
### 5. Enum'ы для статусов

```python
from enum import Enum

class LeakStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    ERROR = "error"

class ProcessingStatus(Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
# Внешние системы
# Внутренние компоненты

| Компонент | Назначение | Технология |
|-----------|------------|-------------|
| API сервер | Прием запросов, управление задачами | FastAPI, Uvicorn |
| Worker | Фоновая обработка видео | Python, threading |
| Модель детекции | Анализ тепловизионных изображений | PyTorch, ResNet18 |
| Видео процессор | Извлечение кадров из видео | OpenCV |
| Репозиторий | Хранение результатов | SQLite / PostgreSQL |

## Внешние системы (третьи стороны)

| Система | Назначение | Взаимодействие |
|---------|------------|----------------|
| PostgreSQL | Хранение результатов детекций | SQLAlchemy / asyncpg |
| Redis | Кэширование и брокер сообщений | redis-py |
| Airflow | Оркестрация батчевой обработки | DockerOperator |
| Nginx | Reverse proxy и балансировка | HTTP проксирование |
| Docker | Контейнеризация сервисов | Docker SDK |

## Внешние устройства

| Устройство | Назначение | Взаимодействие |
|------------|------------|----------------|
| Дрон | Сбор видео, спуск для подтверждения | API запросы |
| Тепловизор | Съемка тепловизионных видео | Передача файлов |
| RGB камера | Съемка обычного видео | Передача файлов |
| Газоанализатор | Подтверждение утечки на месте | Через дрон |

# Батчевый сервис

## Типы задач

| Тип задачи | Описание | Где используется |
|------------|----------|------------------|
| check_for_new_videos | Проверяет наличие новых видео | Airflow DAG |
| backfill_processed_videos | Восстанавливает состояние обработанных видео | Airflow DAG, backfill.py |
| process_videos_batch | Запускает Docker контейнер с обработкой | Airflow DAG (DockerOperator) |
| process_single_video | Обрабатывает одно видео через API | API endpoint |
| process_directory_batch | Обрабатывает всю директорию с видео | CLI, Use Case |

## Передача секретов

Секреты передаются через переменные окружения:

```bash
# .env файл
ENVIRONMENT=production
LOG_LEVEL=INFO
USE_GPU=false
DATABASE_URL=postgresql://user:password@postgres:5432/gas_leak
REDIS_URL=redis://redis:6379/0

# GAZ_LEAK_V2 - Детектор утечек газа

## Airflow DAG Пример

```python
DockerOperator(
    environment={
        'DATABASE_URL': Variable.get('DATABASE_URL'),
    }
)

# Пошаговая установка

## Требования

| Компонент | Версия | Проверка |
|-----------|--------|----------|
| Python | 3.9 или выше | `python --version` |
| pip | 23.0 или выше | `pip --version` |
| Git | любая | `git --version` |

## Шаг 1: Клонирование репозитория

```bash
git clone https://github.com/Evgeniy3252834/GAZ_LEAK_V2.git
cd GAZ_LEAK_V2

## Шаг 2: Создание виртуального окружения

Windows (Command Prompt или PowerShell):

`python -m venv venv`
`venv\Scripts\activate.bat`

Windows (Git Bash):

`python -m venv venv`
`source venv/Scripts/activate`

macOS / Linux:

`python3 -m venv venv`
`source venv/bin/activate`

## Шаг 3: Установка зависимостей

`pip install --upgrade pip`
`pip install -r requirements/base.txt`

## Шаг 4: Настройка переменных окружения

`cp .env.example .env`

Содержимое `.env` (можно оставить по умолчанию):

`ENVIRONMENT=development`
`LOG_LEVEL=INFO`
`USE_GPU=false`
`DATABASE_URL=sqlite:///./gas_leak.db`
`REDIS_URL=redis://localhost:6379/0`

## Шаг 5: Загрузка модели

Способ 1 - через gdown (рекомендуется):

`pip install gdown`
`gdown "https://drive.google.com/uc?id=1oPftKdKgtSaGc9__v9eoGHnhqM5JcHWk" -O models/thermal_model.pth`

Способ 2 - вручную:

Скачайте модель по ссылке: https://drive.google.com/file/d/1oPftKdKgtSaGc9__v9eoGHnhqM5JcHWk/view
Поместите файл в папку models/
Переименуйте в thermal_model.pth (если нужно)

Способ 3 - тестовая модель:

`python -c "`
`import torch`
`import torch.nn as nn`
`import torchvision.models as models`

`class ThermalLeakDetector(nn.Module):`
`    def __init__(self):`
`        super().__init__()`
`        self.model = models.resnet18(weights=None)`
`        self.model.fc = nn.Linear(self.model.fc.in_features, 2)`
`    `
`    def forward(self, x):`
`        return self.model(x)`

`torch.save(ThermalLeakDetector().state_dict(), 'models/thermal_model.pth')`
`print('✅ Тестовая модель создана')`
`"`

## Шаг 6: Создание директорий для данных

`mkdir -p data/input_videos`
`mkdir -p data/processed`
`mkdir -p data/results`
`mkdir -p logs`

## Шаг 7: Проверка установки

`python -c "`
`import sys`
`sys.path.insert(0, '.')`
`from src.infrastructure.model_inference import PyTorchModelInference`
`print('✅ Все зависимости установлены корректно')`
`"`

## Запуск

Быстрый запуск (API сервер):

`python src/main.py --mode api`

Ожидаемый вывод:

`INFO:     Started server process [xxxxx]`
`INFO:     Waiting for application startup.`
`INFO:     Application startup complete.`
`INFO:     Uvicorn running on http://0.0.0.0:8000`

Запуск воркера:

`python src/main.py --mode worker`

Запуск батчевой обработки:

`python src/main.py --mode batch --input-dir ./data/input_videos --output-dir ./data/results`

Проверка работы API:

`curl http://localhost:8000/health`

Ожидаемый ответ:

`{"status":"healthy","timestamp":"2024-01-01T12:00:00.000000"}`

Запуск через Docker:

`docker build -f docker/Dockerfile.app -t gas-leak-detector:latest .`
`docker run -d --name gas-leak-api -p 8000:8000 -v $(pwd)/data:/data -v $(pwd)/models:/app/models gas-leak-detector:latest`
`curl http://localhost:8000/health`
`docker stop gas-leak-api && docker rm gas-leak-api`

## API Эндпоинты

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | /health | Проверка здоровья сервиса |
| GET | /docs | Swagger документация |
| GET | /openapi.json | OpenAPI схема |
| POST | /api/v1/process/video | Обработка одного видео |
| POST | /api/v1/batch/process | Батчевая обработка |
| GET | /api/v1/detections | Получение результатов |

## Примеры запросов

Обработка одного видео:

`curl -X POST "http://localhost:8000/api/v1/process/video?video_path=data/input_videos/test.mp4"`

Батчевая обработка:

`curl -X POST "http://localhost:8000/api/v1/batch/process" \`
`  -H "Content-Type: application/json" \`
`  -d '{"video_paths": ["video1.mp4", "video2.mp4"], "callback_url": "https://example.com/callback"}'`

Получение результатов:

`curl "http://localhost:8000/api/v1/detections?limit=10"`

## Тестирование

Покрытие тестами: 73%

| Компонент | Покрытие | Тестов |
|-----------|----------|--------|
| API (batch_api.py) | 91% | 11 |
| Domain Entities | 98% | 5 |
| Use Cases (batch_process) | 92% | 2 |
| Use Cases (detect_leak) | 90% | 3 |
| Model Inference | 95% | 3 |
| Repository | 98% | 4 |
| ИТОГО | 73% | 32 |

Запуск тестов:

`pytest tests/unit/ -v`
`pytest tests/unit/ --cov=src --cov-report=term`

## Docker

Образы:

| Образ | Назначение | Dockerfile |
|-------|------------|------------|
| gas-leak-detector:latest | Основной образ приложения | docker/Dockerfile.app |

Полный стек (Docker Compose):

| Сервис | Порт | Назначение |
|--------|------|------------|
| api | 8000 | API сервер |
| worker | - | Фоновый воркер |
| postgres | 5432 | База данных |
| redis | 6379 | Кэш и брокер |
| airflow-webserver | 8080 | Airflow UI |
| nginx | 80 | Reverse proxy |

`cd docker`
`docker-compose -f docker-compose.full.yml up -d`
`docker-compose -f docker-compose.full.yml ps`
`docker-compose -f docker-compose.full.yml down`

## Airflow DAG

Структура DAG:

`gas_leak_detection_batch (каждые 15 минут)`
`├── check_for_new_videos     # Проверка новых видео`
`├── backfill_processed_videos # Бэкфилл`
`├── process_videos_batch      # DockerOperator обработка`
`└── cleanup_old_videos        # Очистка старых файлов`

Настройка Airflow:

`pip install apache-airflow`
`airflow db init`
`airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com`
`cp dags/gas_leak_detection_dag.py ~/airflow/dags/`
`airflow webserver -p 8080`
`airflow scheduler`

## Идемпотентность и Бэкфилл

Механизм идемпотентности:

`# Структура`
`data/processed/`
`├── video1.mp4.done`
`├── video2.mp4.done`
`└── video3.mp4.done`

Бэкфилл:

`python scripts/backfill.py --input-dir ./data/input_videos --output-dir ./data/results`

Результат - манифест:

`{`
`  "backfill_timestamp": "2024-01-01T12:00:00",`
`  "total_videos": 10,`
`  "processed_count": 7,`
`  "failed_count": 1,`
`  "videos": [...]`
`}`

## Переменные окружения (Config.py)

| Переменная | Описание | Значение по умолчанию |
|------------|----------|----------------------|
| ENVIRONMENT | Среда запуска | development |
| LOG_LEVEL | Уровень логирования | INFO |
| USE_GPU | Использовать GPU | false |
| DATABASE_URL | URL подключения к БД | sqlite:///./gas_leak.db |
| REDIS_URL | URL подключения к Redis | redis://localhost:6379/0 |
| CONFIDENCE_THRESHOLD | Порог уверенности модели | 0.5 |
| BATCH_SIZE | Размер батча для обработки | 32 |
| IMAGE_SIZE | Размер входного изображения | (224, 224) |
| MAX_WORKERS | Максимум воркеров | 4 |
| PROCESSING_INTERVAL | Интервал обработки (сек) | 300 |

Использование в коде:

`from config.config import config`

`print(config.model.confidence_threshold)  # 0.5`
`print(config.model.device)                 # 'cpu' или 'cuda'`
`print(config.batch.supported_formats)      # ('.mp4', '.avi', '.mov')`
