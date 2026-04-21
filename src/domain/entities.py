from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
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

@dataclass
class VideoFrame:
    timestamp: datetime
    thermal_image: bytes
    rgb_image: Optional[bytes] = None
    frame_index: int = 0
    video_path: str = ""

@dataclass
class LeakDetectionResult:
    frame_id: str
    timestamp: datetime
    leak_probability: float
    is_leak: bool
    confidence: float
    video_path: str = ""
    bounding_box: Optional[tuple] = None
    
    def to_dict(self) -> dict:
        return {
            "frame_id": self.frame_id,
            "timestamp": self.timestamp.isoformat(),
            "leak_probability": self.leak_probability,
            "is_leak": self.is_leak,
            "confidence": self.confidence,
            "video_path": self.video_path,
            "bounding_box": self.bounding_box
        }

@dataclass
class BatchJob:
    job_id: str
    video_paths: List[str]
    status: ProcessingStatus
    created_at: datetime
    updated_at: datetime
    results: List[LeakDetectionResult] = field(default_factory=list)
    error_message: Optional[str] = None

@dataclass
class LeakConfirmation:
    leak_id: str
    detection_result: LeakDetectionResult
    confirmed: bool
    gas_concentration: Optional[float] = None
    confirmed_at: datetime = field(default_factory=datetime.now)
    status: LeakStatus = LeakStatus.PENDING
