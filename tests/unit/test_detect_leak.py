import pytest
from unittest.mock import Mock, MagicMock
from pathlib import Path
from datetime import datetime

from src.domain.entities import LeakDetectionResult, VideoFrame
from src.usecases.detect_leak import DetectLeakUseCase

class TestDetectLeakUseCase:
    @pytest.fixture
    def mock_model(self):
        model = Mock()
        model.predict.return_value = {
            'leak_probability': 0.8,
            'is_leak': True,
            'confidence': 0.8
        }
        return model
    
    @pytest.fixture
    def mock_video_processor(self):
        processor = Mock()
        frame = VideoFrame(
            timestamp=datetime.now(),
            thermal_image=b'test_image_data',
            frame_index=0
        )
        processor.extract_frames.return_value = [frame]
        return processor
    
    @pytest.fixture
    def mock_repository(self):
        return Mock()
    
    def test_process_video_detects_leak(self, mock_model, mock_video_processor, mock_repository):
        usecase = DetectLeakUseCase(
            model=mock_model,
            video_processor=mock_video_processor,
            repository=mock_repository,
            confidence_threshold=0.5
        )
        
        results = usecase.process_video(Path("test_video.mp4"))
        
        assert len(results) > 0
        assert results[0].is_leak == True
        assert results[0].leak_probability == 0.8
        mock_repository.save_detection.assert_called_once()
    
    def test_process_video_no_leak_below_threshold(self, mock_model, mock_video_processor, mock_repository):
        mock_model.predict.return_value = {
            'leak_probability': 0.3,
            'is_leak': False,
            'confidence': 0.7
        }
        
        usecase = DetectLeakUseCase(
            model=mock_model,
            video_processor=mock_video_processor,
            repository=mock_repository,
            confidence_threshold=0.5
        )
        
        results = usecase.process_video(Path("test_video.mp4"))
        
        assert len(results) == 0
        mock_repository.save_detection.assert_not_called()
    
    def test_process_batch(self, mock_model, mock_video_processor, mock_repository):
        usecase = DetectLeakUseCase(
            model=mock_model,
            video_processor=mock_video_processor,
            repository=mock_repository,
            confidence_threshold=0.5
        )
        
        video_paths = [Path(f"video_{i}.mp4") for i in range(3)]
        job = usecase.process_batch(video_paths)
        
        assert job.job_id is not None
        assert len(job.video_paths) == 3
        mock_repository.save_batch_job.assert_called_once()
