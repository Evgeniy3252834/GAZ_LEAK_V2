import pytest
from unittest.mock import Mock
from pathlib import Path
from datetime import datetime

from src.usecases.batch_process import BatchProcessUseCase
from src.domain.entities import BatchJob, ProcessingStatus, LeakDetectionResult

class TestBatchProcessUseCase:
    @pytest.fixture
    def mock_detect_leak(self):
        mock = Mock()
        mock.process_video.return_value = [
            LeakDetectionResult(
                frame_id="test_1",
                timestamp=datetime.now(),
                leak_probability=0.9,
                is_leak=True,
                confidence=0.9,
                video_path="test.mp4"
            )
        ]
        return mock
    
    def test_process_directory_idempotent(self, tmp_path, mock_detect_leak):
        # Создаем тестовые видео
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        output_dir = tmp_path / "output"
        
        video_file = input_dir / "test1.mp4"
        video_file.touch()
        
        # Создаем файл .done для имитации уже обработанного видео
        done_file = output_dir / "test1.mp4.done"
        done_file.parent.mkdir(exist_ok=True)
        done_file.touch()
        
        batch_processor = BatchProcessUseCase(
            detect_leak_usecase=mock_detect_leak,
            max_workers=1
        )
        
        # Обрабатываем директорию
        batch_processor.process_directory(input_dir, output_dir)
        
        # Проверяем, что process_video не был вызван для уже обработанного видео
        mock_detect_leak.process_video.assert_not_called()
