# 🔍 Gas Leak Detection System

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-blue?logo=opencv&logoColor=white)](https://opencv.org/)
[![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker&logoColor=white)](https://www.docker.com/)
[![Airflow](https://img.shields.io/badge/Airflow-2.5+-orange?logo=apacheairflow&logoColor=white)](https://airflow.apache.org/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Nginx](https://img.shields.io/badge/Nginx-009639?logo=nginx&logoColor=white)](https://nginx.org/)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-2088FF?logo=githubactions&logoColor=white)](https://github.com/features/actions)
[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

Система детекции утечек газа с помощью дронов, использующая компьютерное зрение для анализа тепловизионных изображений.

---

## 📖 Краткое описание логики

Дрон летит над трубопроводом и записывает видео с тепловизора. Видео передается в систему, где нейросетевая модель (ResNet18) анализирует каждый кадр. Модель определяет наличие шлейфа газа и выдает вероятность утечки от 0 до 1. Если вероятность превышает порог 0.5, система фиксирует потенциальную утечку и отправляет дрон на подтверждение газоанализатором.

### 🏗️ Архитектура

Проект построен на **чистой архитектуре (Clean Architecture)** с разделением на независимые слои:

| Слой | Назначение | Расположение |
|------|-----------|--------------|
| **Domain** | Сущности и интерфейсы | `src/domain/` |
| **Use Cases** | Бизнес-логика | `src/usecases/` |
| **Infrastructure** | Реализации (модель, видео, БД) | `src/infrastructure/` |
| **API** | REST эндпоинты | `src/api/` |
| **CLI** | Командная строка | `src/cli/` |

### 🛠️ Технологический стек

| Компонент | Технология |
|-----------|------------|
| Язык | Python 3.12 |
| ML фреймворк | PyTorch, ResNet18 |
| Обработка видео | OpenCV |
| API сервер | FastAPI, Uvicorn |
| База данных | SQLite / PostgreSQL |
| Оркестрация | Apache Airflow |
| Контейнеризация | Docker, Docker Compose |

## 🖥️ Как воспроизвести результат (локальный запуск)

### Требования

| Компонент | Версия | Проверка |
|-----------|--------|----------|
| Python | 3.9 или выше | `python --version` |
| Git | любая | `git --version` |
| pip | 23.0 или выше | `pip --version` |

### Пошаговая инструкция

#### Шаг 1: Клонирование репозитория

```bash
git clone https://github.com/Evgeniy3252834/GAZ_LEAK_V2.git
cd GAZ_LEAK_V2```

#### Шаг 2: Создание виртуального окружения

Windows (Command Prompt):

```cmd
python -m venv venv
venv\Scripts\activate.bat```

Windows (Git Bash):

```bash
python -m venv venv
source venv/Scripts/activate```

macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate```

#### Шаг 3: Установка зависимостей

```bash
pip install --upgrade pip
pip install -r requirements/base.txt```

#### Шаг 4: Настройка переменных окружения

```bash
cp .env.example .env```

#### Шаг 5: Загрузка модели

##### Способ 1 - через gdown (рекомендуется):
```bash
pip install gdown
gdown "https://drive.google.com/uc?id=1oPftKdKgtSaGc9__v9eoGHnhqM5JcHWk" -O models/thermal_model.pth```

##### Способ 2 - вручную:
- Скачайте модель по ссылке: https://drive.google.com/file/d/1oPftKdKgtSaGc9__v9eoGHnhqM5JcHWk/view

- Поместите файл в папку models/

- Переименуйте в thermal_model.pth (если нужно)

#### Шаг 6: Создание директорий для данных

```bash
mkdir -p data/input_videos data/processed data/results logs```

#### Шаг 7: Запуск API сервера

```bash
python src/main.py --mode api```
**Ожидаемый вывод:**
INFO: Started server process [xxxxx]
INFO: Uvicorn running on http://0.0.0.0:8000

#### Шаг 8: Проверка работы API

Через curl:

```bash
curl http://localhost:8000/health```

Через браузер:
Откройте http://localhost:8000/health

Ожидаемый ответ:

```json
{"status":"healthy","timestamp":"2026-04-23T20:37:57.949452"}```

#### Шаг 9: Запуск тестов (проверка покрытия)

```bash
pytest tests/unit/ -v --cov=src --cov-report=term```

Ожидаемый результат:

Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
src/api/batch_api.py                      68      6    91%
src/domain/entities.py                    49      1    98%
src/usecases/batch_process.py             50      4    92%
src/usecases/detect_leak.py               48      5    90%
src/infrastructure/model_inference.py     55      3    95%
src/infrastructure/repository.py          55      1    98%
-----------------------------------------------------------
TOTAL                                    491    146    73%

============================== 32 passed in 5.78s ==============================

## 🚀 Как задеплоить на сервер

### Требования к серверу

| Параметр | Рекомендация |
|----------|--------------|
| ОС | Ubuntu 22.04 или 24.04 LTS |
| RAM | 4-8 ГБ |
| CPU | 2-4 ядра |
| Диск | 40-80 ГБ SSD |

### Пошаговая инструкция деплоя

#### Шаг 1: Подключение к серверу

```bash
ssh root@89.108.78.157```

#### Шаг 2: Установка Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
apt install docker-compose-plugin -y

docker --version
docker compose version```

#### Шаг 3: Клонирование проекта

```bash
cd /opt
git clone https://github.com/Evgeniy3252834/GAZ_LEAK_V2.git gas-leak
cd gas-leak```

#### Шаг 4: Установка Python и зависимостей

```bash
apt install python3-pip -y
pip install -r requirements/base.txt --break-system-packages
pip install opencv-python-headless --break-system-packages```

#### Шаг 5: Загрузка модели

```bash
pip install gdown --break-system-packages
gdown "https://drive.google.com/uc?id=1oPftKdKgtSaGc9__v9eoGHnhqM5JcHWk" -O models/thermal_model.pth```

#### Шаг 6: Настройка окружения

```bash
mkdir -p data/input_videos data/processed data/results logs

cp .env.example .env```

#### Шаг 7: Запуск API сервера

##### Вариант А: Запуск в фоне (рекомендуется)
```bash
nohup python3 -m src.main --mode api > logs/api.log 2>&1 &```

##### Вариант Б: Запуск через systemd (автозапуск после перезагрузки)
```bash
cat > /etc/systemd/system/gas-leak-api.service << 'EOF'
[Unit]
Description=Gas Leak Detection API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/gas-leak
ExecStart=/usr/bin/python3 -m src.main --mode api
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable gas-leak-api
systemctl start gas-leak-api```

##### Вариант В: Запуск через Docker Compose (полный стек)
```bash
docker compose -f docker/docker-compose.full.yml up -d```

#### Шаг 8: Проверка работоспособности

```bash
curl http://localhost:8000/health```

**{"status":"healthy","timestamp":"2026-04-23T20:37:57.949452"}**

#### Шаг 9: Доступ из браузера

Сервис	URL
API сервер	http://89.108.78.157:8000
Health check	http://89.108.78.157:8000/health
Swagger документация	http://89.108.78.157:8000/docs
Полезные команды для управления
```bash
tail -f /opt/gas-leak/logs/api.log

systemctl status gas-leak-api

systemctl restart gas-leak-api

pkill -f "src.main"

ps aux | grep python```

### 🛠️ Устранение неполадок

| Проблема | Решение |
|----------|---------|
| Порт 8000 уже занят | `lsof -i :8000` → `kill -9 <PID>` |
| Ошибка импорта `cv2` | `pip install opencv-python-headless --break-system-packages` |
| Модель не загружается | Проверить: `ls -la models/thermal_model.pth` |
| Нет доступа к порту извне | Открыть порт: `ufw allow 8000` |
| `ModuleNotFoundError: No module named 'src'` | `export PYTHONPATH="${PYTHONPATH}:$(pwd)"` |
| Процесс умирает после закрытия SSH | Использовать `nohup` или systemd сервис |
| Docker образ не собирается | Использовать `opencv-python-headless` вместо `opencv-python` |
| Ошибка `address already in use` | `pkill -f "src.main"` → запустить заново |
| Тесты не проходят | `pip install pytest pytest-cov --break-system-packages` |
| `gdown` не скачивает модель | Скачать вручную по ссылке: https://drive.google.com/file/d/1oPftKdKgtSaGc9__v9eoGHnhqM5JcHWk/view |

## 📁 Структура проекта
GAZ_LEAK_V2/
│
├── .github/workflows/ > CI/CD пайплайны GitHub Actions
│ └── deploy.yml > Автоматический деплой на сервер
│
├── config/ > Конфигурация проекта
│ ├── init.py
│ └── config.py > Централизованный конфиг (все переменные)
│
├── dags/ > Airflow DAG для оркестрации
│ └── gas_leak_detection_dag.py
│
├── docker/ > Docker файлы для контейнеризации
│ ├── Dockerfile.app > Образ приложения
│ ├── docker-compose.full.yml > Полный стек (API, worker, БД, Redis, Airflow, Nginx)
│ └── nginx.conf > Reverse proxy конфигурация
│
├── models/ > Обученные модели
│ └── thermal_model.pth > Веса модели ResNet18 (44 MB)
│
├── requirements/ > Зависимости Python
│ ├── base.txt > Основные зависимости
│ ├── dev.txt > Для разработки (тесты, линтеры)
│ └── prod.txt > Для production
│
├── scripts/ > Вспомогательные скрипты
│ ├── backfill.py > Бэкфилл (восстановление состояния)
│ ├── deploy.sh > Скрипт деплоя
│ └── run_checks.sh > Проверка системы
│
├── src/ > Исходный код (Clean Architecture)
│ ├── init.py
│ │
│ ├── api/ > API слой (входные данные)
│ │ ├── init.py
│ │ └── batch_api.py > FastAPI эндпоинты
│ │
│ ├── cli/ > CLI слой (командная строка)
│ │ ├── init.py
│ │ └── batch_process.py > CLI для батчевой обработки
│ │
│ ├── domain/ > Domain слой (ядро бизнес-логики)
│ │ ├── init.py
│ │ ├── entities.py > Бизнес-сущности
│ │ └── interfaces.py > Абстракции (порт)
│ │
│ ├── infrastructure/ > Infrastructure слой (реализации)
│ │ ├── init.py
│ │ ├── model_inference.py > PyTorch модель
│ │ ├── repository.py > SQLite / PostgreSQL хранилище
│ │ └── video_processor.py > OpenCV обработка видео
│ │
│ ├── usecases/ > Use Cases слой (бизнес-логика)
│ │ ├── init.py
│ │ ├── batch_process.py > Батчевая обработка
│ │ └── detect_leak.py > Детекция утечки
│ │
│ └── main.py > Точка входа (CLI аргументы)
│
├── tests/ > Тесты
│ ├── init.py
│ ├── unit/ > Юнит-тесты (32 теста)
│ │ ├── test_batch_process.py
│ │ ├── test_detect_leak.py
│ │ ├── test_model_inference.py
│ │ ├── test_repository.py
│ │ ├── test_api_endpoints.py
│ │ └── ...
│ └── fixtures/ > Тестовые данные
│ └── test_image.png
│
├── data/ > Данные (создаётся при запуске)
│ ├── input_videos/ > Видео для обработки
│ ├── processed/ > Маркеры обработанных видео (.done)
│ └── results/ > Результаты детекции
│
├── logs/ > Логи приложения
│
├── .env.example > Пример переменных окружения
├── .gitignore
├── Makefile
└── README.md

## Направление зависимостей (по Clean Architecture)
Внешний мир (HTTP/CLI) → API/CLI → Use Cases → Domain
↓
Infrastructure (реализации)

**Правило:** Зависимости идут только внутрь. Domain слой НЕ зависит от API, CLI или Infrastructure.

## 📊 Тестирование

### Что проверяют тесты

| Тест | Что проверяет |
|------|---------------|
| `test_batch_process.py` | Идемпотентность, обработку новых видео, пропуск уже обработанных |
| `test_detect_leak.py` | Детекцию утечки, порог срабатывания (0.5), батчевую обработку |
| `test_model_inference.py` | Загрузку модели, предсказание на одном изображении, батчевый инференс |
| `test_repository.py` | Сохранение детекций, сохранение батчевых задач, получение pending задач, обновление статусов |
| `test_api_endpoints.py` | Health check, Swagger документацию, обработку видео, батчевую обработку, получение результатов |

### Покрытие кода тестами

**Итоговое покрытие: 73%** (выше требуемых 70%)

| Компонент | Покрытие |
|-----------|----------|
| API (batch_api.py) | 91% |
| Domain Entities | 98% |
| Use Cases (batch_process) | 92% |
| Use Cases (detect_leak) | 90% |
| Model Inference | 95% |
| Repository | 98% |
| **TOTAL** | **73%** |

## 📄 Лицензия

MIT License

Copyright (c) 2026 Evgeniy

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 🔗 Ссылка на репозиторий

**GitHub:** [Evgeniy3252834/GAZ_LEAK_V2](https://github.com/Evgeniy3252834/GAZ_LEAK_V2)

---

© 2026 Gas Leak Detection Team
