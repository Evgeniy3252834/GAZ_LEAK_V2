import pytest
import cv2
import numpy as np
from pathlib import Path
import tempfile
import time
import os
import sys

# Пропускаем на Windows
pytestmark = pytest.mark.skipif(
    sys.platform == "win32",
    reason="Video processor full tests skipped on Windows (codec issues)"
)

class TestOpenCVVideoProcessorFull:
    
    @pytest.fixture
    def sample_video(self):
        """Создание тестового видео"""
        fd, path = tempfile.mkstemp(suffix='.avi')
        os.close(fd)
        
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        out = cv2.VideoWriter(path, fourcc, 5.0, (224, 224))
        
        if not out.isOpened():
            pytest.skip("Cannot create video writer")
        
        for i in range(10):
            frame = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            out.write(frame)
        
        out.release()
        time.sleep(0.5)
        
        yield Path(path)
        
        time.sleep(0.3)
        if os.path.exists(path):
            try:
                os.unlink(path)
            except PermissionError:
                pass

    def test_extract_frames_with_real_video(self, sample_video):
        from src.infrastructure.video_processor import OpenCVVideoProcessor
        processor = OpenCVVideoProcessor()
        frames = processor.extract_frames(sample_video, interval_sec=0.5)
        assert isinstance(frames, list)

    def test_get_video_metadata_real(self, sample_video):
        from src.infrastructure.video_processor import OpenCVVideoProcessor
        processor = OpenCVVideoProcessor()
        metadata = processor.get_video_metadata(sample_video)
        assert metadata['width'] == 224
        assert metadata['height'] == 224
