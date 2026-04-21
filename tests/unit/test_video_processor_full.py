import pytest
import cv2
import numpy as np
from pathlib import Path
import tempfile
from src.infrastructure.video_processor import OpenCVVideoProcessor

class TestOpenCVVideoProcessorFull:
    
    @pytest.fixture
    def sample_video(self):
        """Создание тестового видео"""
        fd, path = tempfile.mkstemp(suffix='.mp4')
        
        # Создаем видео с 10 кадрами
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(path, fourcc, 1.0, (224, 224))
        
        for i in range(10):
            frame = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            out.write(frame)
        
        out.release()
        yield Path(path)
        
        # Чистим
        import os
        if os.path.exists(path):
            os.unlink(path)
    
    def test_extract_frames_with_real_video(self, sample_video):
        """Тест извлечения кадров из реального видео"""
        processor = OpenCVVideoProcessor()
        frames = processor.extract_frames(sample_video, interval_sec=0.5)
        
        assert len(frames) > 0
        assert frames[0].frame_index == 0
        assert frames[0].thermal_image is not None
        assert frames[0].video_path == str(sample_video)
    
    def test_get_video_metadata_real(self, sample_video):
        """Тест получения метаданных реального видео"""
        processor = OpenCVVideoProcessor()
        metadata = processor.get_video_metadata(sample_video)
        
        assert metadata['width'] == 224
        assert metadata['height'] == 224
        assert metadata['fps'] == 1.0
        assert metadata['frame_count'] == 10
        assert metadata['duration'] == 10.0
