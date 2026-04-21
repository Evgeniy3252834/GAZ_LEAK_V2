FROM python:3.9-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements
COPY requirements/base.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Копируем код
COPY src/ ./src/
COPY config/ ./config/
COPY models/ ./models/
COPY scripts/ ./scripts/

# Создаем директории для данных
RUN mkdir -p /data/{input_videos,processed,results} /app/logs

ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

CMD ["python", "-m", "src.cli.batch_process", "--input-dir", "/data/input_videos", "--output-dir", "/data/results"]
