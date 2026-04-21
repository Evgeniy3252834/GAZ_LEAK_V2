from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from pathlib import Path
from PIL import Image
from .entities import VideoFrame, LeakDetectionResult, BatchJob, LeakConfirmation

class ModelInferenceInterface(ABC):
    @abstractmethod
    def predict(self, image: Image.Image) -> Dict:
        pass
    
    @abstractmethod
    def predict_batch(self, images: List[Image.Image]) -> List[Dict]:
        pass

class VideoProcessorInterface(ABC):
    @abstractmethod
    def extract_frames(self, video_path: Path, interval_sec: float = 1.0) -> List[VideoFrame]:
        pass
    
    @abstractmethod
    def get_video_metadata(self, video_path: Path) -> Dict:
        pass

class GasAnalyzerInterface(ABC):
    @abstractmethod
    def confirm_leak(self, detection: LeakDetectionResult, location: tuple) -> LeakConfirmation:
        pass

class RepositoryInterface(ABC):
    @abstractmethod
    def save_detection(self, detection: LeakDetectionResult) -> str:
        pass
    
    @abstractmethod
    def save_batch_job(self, job: BatchJob) -> str:
        pass
    
    @abstractmethod
    def get_pending_jobs(self) -> List[BatchJob]:
        pass
    
    @abstractmethod
    def update_job_status(self, job_id: str, status: str, results: List = None):
        pass
