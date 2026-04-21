import logging
from pathlib import Path
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from .detect_leak import DetectLeakUseCase
from src.domain.entities import BatchJob, ProcessingStatus

logger = logging.getLogger(__name__)

class BatchProcessUseCase:
    def __init__(self, detect_leak_usecase: DetectLeakUseCase, max_workers: int = 4):
        self.detect_leak = detect_leak_usecase
        self.max_workers = max_workers
    
    def process_directory(self, input_dir: Path, output_dir: Path) -> List[BatchJob]:
        """Идемпотентная обработка директории с видео"""
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Получаем список видео
        video_files = []
        for ext in ['*.mp4', '*.avi', '*.mov']:
            video_files.extend(input_dir.glob(ext))
        
        # Фильтруем уже обработанные (идемпотентность)
        pending_videos = []
        for video in video_files:
            done_file = output_dir / f"{video.name}.done"
            if not done_file.exists():
                pending_videos.append(video)
        
        if not pending_videos:
            logger.info("No pending videos to process")
            return []
        
        logger.info(f"Processing {len(pending_videos)} videos")
        
        # Параллельная обработка
        jobs = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_video = {
                executor.submit(self.detect_leak.process_video, video): video 
                for video in pending_videos
            }
            
            for future in as_completed(future_to_video):
                video = future_to_video[future]
                try:
                    results = future.result()
                    # Отмечаем как обработанное
                    done_file = output_dir / f"{video.name}.done"
                    done_file.touch()
                    
                    # Создаем отчет
                    report_file = output_dir / f"{video.name}_report.txt"
                    with open(report_file, 'w') as f:
                        f.write(f"Video: {video.name}\n")
                        f.write(f"Processed at: {datetime.now()}\n")
                        f.write(f"Leaks found: {len(results)}\n")
                        for res in results:
                            f.write(f"  - {res.timestamp}: {res.leak_probability:.2f}\n")
                    
                    logger.info(f"Successfully processed {video.name}")
                except Exception as e:
                    logger.error(f"Failed to process {video.name}: {e}")
                    error_file = output_dir / f"{video.name}.error"
                    error_file.write_text(str(e))
        
        return jobs
