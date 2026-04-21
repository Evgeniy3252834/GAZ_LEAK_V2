#!/usr/bin/env python
"""
Main entry point for Gas Leak Detection System
"""
import argparse
import logging
import sys
from pathlib import Path

from config.config import config

def setup_logging():
    """Настройка логирования"""
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.logs_dir / "service.log"),
            logging.StreamHandler()
        ]
    )

def run_api():
    """Запуск API сервера"""
    import uvicorn
    from src.api.batch_api import app
    
    logging.info("Starting Gas Leak Detection API server")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level=config.log_level.lower()
    )

def run_batch():
    """Запуск батчевой обработки"""
    from src.cli.batch_process import main
    main()

def run_worker():
    """Запуск воркера для фоновой обработки"""
    import time
    from src.usecases.batch_process import BatchProcessUseCase
    from src.infrastructure.model_inference import PyTorchModelInference
    from src.infrastructure.video_processor import OpenCVVideoProcessor
    from src.infrastructure.repository import SQLiteRepository
    from src.usecases.detect_leak import DetectLeakUseCase
    
    logging.info("Starting background worker")
    
    # Инициализация
    model = PyTorchModelInference()
    video_processor = OpenCVVideoProcessor()
    repository = SQLiteRepository()
    detect_leak = DetectLeakUseCase(model, video_processor, repository)
    batch_processor = BatchProcessUseCase(detect_leak, max_workers=2)
    
    # Мониторинг новых видео
    input_dir = config.data_dir / "input_videos"
    output_dir = config.results_dir
    
    while True:
        try:
            batch_processor.process_directory(input_dir, output_dir)
            time.sleep(config.batch.processing_interval)
        except KeyboardInterrupt:
            logging.info("Worker stopped by user")
            break
        except Exception as e:
            logging.error(f"Worker error: {e}")
            time.sleep(60)

def main():
    parser = argparse.ArgumentParser(description="Gas Leak Detection System")
    parser.add_argument(
        '--mode',
        choices=['api', 'batch', 'worker', 'test'],
        default='api',
        help='Run mode'
    )
    parser.add_argument('--input-dir', type=str, help='Input directory for batch mode')
    parser.add_argument('--output-dir', type=str, help='Output directory for batch mode')
    
    args = parser.parse_args()
    setup_logging()
    
    if args.mode == 'api':
        run_api()
    elif args.mode == 'batch':
        run_batch()
    elif args.mode == 'worker':
        run_worker()
    elif args.mode == 'test':
        # Запуск тестов
        import pytest
        sys.exit(pytest.main(["tests/", "-v", "--cov=src"]))

if __name__ == "__main__":
    main()
