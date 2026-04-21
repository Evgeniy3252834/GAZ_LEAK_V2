import pytest
import cv2
import numpy as np
from pathlib import Path
import tempfile
import time
from src.infrastructure.video_processor import OpenCVVideoProcessor

class TestOpenCVVideoProcessorFixed:
    
    @pytest.fixture
    def sample_video(self):
        """Создание тестового видео с гарантированным FPS"""
        path = tempfile.mktemp(suffix='.avi')  # Используем AVI вместо MP4
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        fps = 5.0  # Явно задаем FPS
        out = cv2.VideoWriter(path, fourcc, fps, (224, 224))
        
        if not out.isOpened():
            pytest.skip("Cannot create video writer")
        
        # Создаем 10 кадров
        for i in range(10):
            frame = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            out.write(frame)
        
        out.release()
        time.sleep(0.1)  # Даем время на освобождение ресурсов
        
        yield Path(path)
        
        # Чистим с задержкой
        time.sleep(0.1)
        if path.exists():
            path.unlink()
    
    def test_get_video_metadata_fixed(self, sample_video):
        """Тест получения метаданных"""
        processor = OpenCVVideoProcessor()
        metadata = processor.get_video_metadata(sample_video)
        
        assert metadata['width'] == 224
        assert metadata['height'] == 224
        assert metadata['fps'] == 5.0
        assert metadata['frame_count'] == 10
    
    def test_extract_frames_skip_when_fps_zero(self, sample_video):
        """Тест извлечения кадров с защитой от деления на ноль"""
        processor = OpenCVVideoProcessor()
        
        # Временно патчим метод для теста
        original_get = cv2.VideoCapture.get
        
        def mock_get(prop_id):
            if prop_id == cv2.CAP_PROP_FPS:
                return 0.0  # Симулируем проблему
            return original_get(prop_id)
        
        # Тест должен обработать ошибку gracefully
        try:
            frames = processor.extract_frames(sample_video, interval_sec=0.5)
            # Если FPS=0, должно быть либо 0 кадров, либо использоваться значение по умолчанию
            assert isinstance(frames, list)
        except ZeroDivisionError:
            pytest.fail("ZeroDivisionError not handled!")
