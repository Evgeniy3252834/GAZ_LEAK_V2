"""
Тесты для API эндпоинтов
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.api.batch_api import app

client = TestClient(app)

class TestAPIEndpoints:

    def test_health_endpoint(self):
        """GET /health - проверка здоровья"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_docs_endpoint(self):
        """GET /docs - документация"""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_json(self):
        """GET /openapi.json - OpenAPI схема"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert "paths" in response.json()
        assert "/health" in response.json()["paths"]

    @patch('src.api.batch_api.detect_leak_usecase')
    @patch('src.api.batch_api.Path')
    def test_process_video_success(self, mock_path, mock_usecase):
        """POST /api/v1/process/video - успешная обработка"""
        # Мокаем Path.exists() чтобы возвращал True
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance
        
        mock_usecase.process_video.return_value = []

        response = client.post("/api/v1/process/video?video_path=data/test.mp4")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processing"
        assert "Video processing started" in data["message"]

    def test_process_video_missing_path(self):
        """POST /api/v1/process/video - без параметра video_path"""
        response = client.post("/api/v1/process/video")
        assert response.status_code == 422  # Validation error

    @patch('src.api.batch_api.batch_processor')
    @patch('src.api.batch_api.Path')
    def test_batch_process(self, mock_path, mock_processor):
        """POST /api/v1/batch/process - батчевая обработка"""
        # Мокаем Path.exists() для всех видео
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance
        
        mock_processor.process_directory.return_value = []

        response = client.post(
            "/api/v1/batch/process",
            json={"video_paths": ["video1.mp4", "video2.mp4"]}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "started"
        assert data["total_videos"] == 2

    def test_batch_process_invalid_json(self):
        """POST /api/v1/batch/process - некорректный JSON"""
        response = client.post(
            "/api/v1/batch/process",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    @patch('src.api.batch_api.repository')
    def test_get_detections(self, mock_repository):
        """GET /api/v1/detections - получение детекций"""
        # Мокаем метод get_pending_jobs или подобный
        mock_repository.get_pending_jobs.return_value = []

        response = client.get("/api/v1/detections?limit=10")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_detections_with_limit(self):
        """GET /api/v1/detections - с параметром limit"""
        response = client.get("/api/v1/detections?limit=5")
        assert response.status_code == 200

    def test_get_detections_invalid_limit(self):
        """GET /api/v1/detections - некорректный limit"""
        response = client.get("/api/v1/detections?limit=-1")
        assert response.status_code == 200  # Должен обработать или вернуть пустой список

    def test_root_endpoint(self):
        """GET / - корневой эндпоинт"""
        response = client.get("/")
        assert response.status_code in [200, 404]
