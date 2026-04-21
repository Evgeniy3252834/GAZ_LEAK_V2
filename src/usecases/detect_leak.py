import logging
from typing import List, Dict
from pathlib import Path
from datetime import datetime
import uuid

from src.domain.entities import (
    LeakDetectionResult, BatchJob, ProcessingStatus, VideoFrame
)
from src.domain.interfaces import (
    ModelInferenceInterface, VideoProcessorInterface, RepositoryInterface
)

logger = logging.getLogger(__name__)

class DetectLeakUseCase:
    def __init__(
        self,
        model: ModelInferenceInterface,
        video_processor: VideoProcessorInterface,
        repository: RepositoryInterface,
        confidence_threshold: float = 0.5
    ):
        self.model = model
        self.video_processor = video_processor
        self.repository = repository
        self.confidence_threshold = confidence_threshold
    
    def process_video(self, video_path: Path, job_id: str = None) -> List[LeakDetectionResult]:
        logger.info(f"Processing video: {video_path}")
        
        frames = self.video_processor.extract_frames(video_path, interval_sec=0.5)
        results = []
        
        for frame in frames:
            from PIL import Image
            import io
            image = Image.open(io.BytesIO(frame.thermal_image))
            prediction = self.model.predict(image)
            
            if prediction['leak_probability'] >= self.confidence_threshold:
                result = LeakDetectionResult(
                    frame_id=f"{video_path.stem}_{frame.frame_index}",
                    timestamp=frame.timestamp,
                    leak_probability=prediction['leak_probability'],
                    is_leak=prediction['is_leak'],
                    confidence=prediction['confidence'],
                    video_path=str(video_path)
                )
                results.append(result)
                self.repository.save_detection(result)
        
        logger.info(f"Found {len(results)} potential leaks in {video_path}")
        return results
    
    def process_batch(self, video_paths: List[Path]) -> BatchJob:
        job_id = str(uuid.uuid4())
        job = BatchJob(
            job_id=job_id,
            video_paths=[str(p) for p in video_paths],
            status=ProcessingStatus.PROCESSING,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.repository.save_batch_job(job)
        all_results = []
        
        try:
            for video_path in video_paths:
                results = self.process_video(video_path, job_id)
                all_results.extend(results)
            
            job.status = ProcessingStatus.COMPLETED
            job.results = all_results
            job.updated_at = datetime.now()
            self.repository.update_job_status(job_id, "completed", all_results)
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            job.status = ProcessingStatus.FAILED
            job.error_message = str(e)
            self.repository.update_job_status(job_id, "failed")
        
        return job
