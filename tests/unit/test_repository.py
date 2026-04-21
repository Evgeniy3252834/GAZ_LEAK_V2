import pytest
import tempfile
import os
from datetime import datetime
from src.infrastructure.repository import SQLiteRepository
from src.domain.entities import LeakDetectionResult, BatchJob, ProcessingStatus

class TestSQLiteRepository:
    
    @pytest.fixture
    def repo(self):
        """Создание временной БД для тестов"""
        # Создаем временный файл с правильными правами
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        
        repo = SQLiteRepository(db_path=path)
        yield repo
        
        # Чистим после тестов
        if os.path.exists(path):
            os.unlink(path)
    
    def test_save_detection(self, repo):
        """Тест сохранения детекции"""
        result = LeakDetectionResult(
            frame_id="test_frame",
            timestamp=datetime.now(),
            leak_probability=0.9,
            is_leak=True,
            confidence=0.9,
            video_path="test.mp4"
        )
        
        detection_id = repo.save_detection(result)
        assert detection_id is not None
        assert detection_id.startswith("det_")
    
    def test_save_batch_job(self, repo):
        """Тест сохранения батчевой задачи"""
        job = BatchJob(
            job_id="test_job",
            video_paths=["video1.mp4", "video2.mp4"],
            status=ProcessingStatus.PROCESSING,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        job_id = repo.save_batch_job(job)
        assert job_id == "test_job"
    
    def test_get_pending_jobs(self, repo):
        """Тест получения ожидающих задач"""
        job = BatchJob(
            job_id="pending_job",
            video_paths=["video.mp4"],
            status=ProcessingStatus.PROCESSING,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        repo.save_batch_job(job)
        pending = repo.get_pending_jobs()
        
        assert len(pending) >= 1
        assert pending[0].job_id == "pending_job"
    
    def test_update_job_status(self, repo):
        """Тест обновления статуса задачи"""
        job = BatchJob(
            job_id="update_job",
            video_paths=["video.mp4"],
            status=ProcessingStatus.PROCESSING,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        repo.save_batch_job(job)
        repo.update_job_status("update_job", "completed")
        
        # Проверяем, что статус обновился
        pending = repo.get_pending_jobs()
        # Задача не должна быть в pending
        assert not any(j.job_id == "update_job" for j in pending)
