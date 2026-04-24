import cv2
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import logging
from PIL import Image
import io

from src.domain.entities import VideoFrame
from src.domain.interfaces import VideoProcessorInterface

logger = logging.getLogger(__name__)

class OpenCVVideoProcessor(VideoProcessorInterface):
    def extract_frames(self, video_path: Path, interval_sec: float = 1.0) -> List[VideoFrame]:
        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Fix для Windows - если fps = 0, используем значение по умолчанию
        if fps <= 0:
            logger.warning(f"Invalid FPS: {fps}, using default 1.0")
            fps = 1.0
        
        frame_interval = int(fps * interval_sec)
        if frame_interval == 0:
            frame_interval = 1
        
        frames = []
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                
                img_byte_arr = io.BytesIO()
                pil_image.save(img_byte_arr, format='PNG')
                
                video_frame = VideoFrame(
                    timestamp=datetime.now(),
                    thermal_image=img_byte_arr.getvalue(),
                    frame_index=frame_count,
                    video_path=str(video_path)
                )
                frames.append(video_frame)
            
            frame_count += 1
        
        cap.release()
        logger.info(f"Extracted {len(frames)} frames from {video_path}")
        return frames
    
    def get_video_metadata(self, video_path: Path) -> Dict:
        cap = cv2.VideoCapture(str(video_path))
        metadata = {
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'duration': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS) if cap.get(cv2.CAP_PROP_FPS) > 0 else 0
        }
        cap.release()
        return metadata
