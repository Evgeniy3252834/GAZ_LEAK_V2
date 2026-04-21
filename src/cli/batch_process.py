#!/usr/bin/env python
import argparse
import logging
import sys
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.infrastructure.model_inference import PyTorchModelInference
from src.infrastructure.video_processor import OpenCVVideoProcessor
from src.infrastructure.repository import SQLiteRepository
from src.usecases.detect_leak import DetectLeakUseCase
from src.usecases.batch_process import BatchProcessUseCase
from config.config import config

def setup_logging(log_level: str = "INFO"):
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    parser = argparse.ArgumentParser(description='Batch video processing for gas leak detection')
    parser.add_argument('--input-dir', type=str, required=True, help='Input directory with videos')
    parser.add_argument('--output-dir', type=str, default='./results', help='Output directory for results')
    parser.add_argument('--model-path', type=str, default=None, help='Path to model weights')
    parser.add_argument('--confidence', type=float, default=0.5, help='Confidence threshold')
    parser.add_argument('--max-workers', type=int, default=4, help='Max parallel workers')
    
    args = parser.parse_args()
    
    setup_logging(config.log_level)
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting batch processing from {args.input_dir}")
    
    # Инициализация зависимостей
    model = PyTorchModelInference(model_path=args.model_path)
    video_processor = OpenCVVideoProcessor()
    repository = SQLiteRepository()
    
    # Use case
    detect_leak = DetectLeakUseCase(
        model=model,
        video_processor=video_processor,
        repository=repository,
        confidence_threshold=args.confidence
    )
    
    batch_processor = BatchProcessUseCase(
        detect_leak_usecase=detect_leak,
        max_workers=args.max_workers
    )
    
    # Обработка
    results = batch_processor.process_directory(
        input_dir=Path(args.input_dir),
        output_dir=Path(args.output_dir)
    )
    
    logger.info(f"Batch processing completed. Processed {len(results)} batches")
    
    # Вывод статистики
    total_leaks = sum(len(job.results) for job in results)
    logger.info(f"Total leaks detected: {total_leaks}")

if __name__ == "__main__":
    main()
