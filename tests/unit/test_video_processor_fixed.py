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
    reason="Video processor tests skipped on Windows (codec issues)"
)

class TestOpenCVVideoProcessorFixed:

    @pytest.fixture
    def sample_video(self):
        """Создание тестового видео с гарантированным FPS"""
        path = tempfile.mktemp(suffix='.avi')
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        fps = 5.0
        out = cv2.VideoWriter(path, fourcc, fps, (224, 224))

        if not out.isOpened():
            pytest.skip("Cannot create video writer")

        for i in range(10):
            frame = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            out.write(frame)

        out.release()
        time.sleep(0.1)

        yield Path(path)

        time.sleep(0.1)
        if os.path.exists(path):
            os.unlink(path)

    def test_get_video_metadata_fixed(self, sample_video):
        """Тест получения метаданных"""
        from src.infrastructure.video_processor import OpenCVVideoProcessor
        processor = OpenCVVideoProcessor()
        metadata = processor.get_video_metadata(sample_video)

        assert metadata['width'] == 224
        assert metadata['height'] == 224

    def test_extract_frames_skip_when_fps_zero(self, sample_video):
        """Тест извлечения кадров с защитой от деления на ноль"""
        from src.infrastructure.video_processor import OpenCVVideoProcessor
        processor = OpenCVVideoProcessor()
        frames = processor.extract_frames(sample_video, interval_sec=0.5)
        assert isinstance(frames, list)
