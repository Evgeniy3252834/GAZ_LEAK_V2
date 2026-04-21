import pytest
import sys
from src.infrastructure.video_processor import OpenCVVideoProcessor

# Пропускаем все тесты видео на Windows из-за проблем с кодеком
pytestmark = pytest.mark.skipif(
    sys.platform == "win32",
    reason="Video processor tests skipped on Windows due to codec issues"
)

class TestOpenCVVideoProcessorSimple:
    
    def test_processor_creation(self):
        """Тест создания процессора"""
        processor = OpenCVVideoProcessor()
        assert processor is not None
    
    def test_metadata_for_nonexistent_file(self):
        """Тест метаданных для несуществующего файла"""
        from pathlib import Path
        processor = OpenCVVideoProcessor()
        # Не должно упасть с ошибкой
        metadata = processor.get_video_metadata(Path("nonexistent_file_12345.mp4"))
        assert isinstance(metadata, dict)
