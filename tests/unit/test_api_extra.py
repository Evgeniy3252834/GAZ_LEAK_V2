import pytest
import sys
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.api.batch_api import app

client = TestClient(app)

# Пропускаем на Windows из-за проблем с асинхронными моками
pytestmark = pytest.mark.skipif(
    sys.platform == "win32",
    reason="Async API tests skipped on Windows"
)

class TestAPIExtra:
    @patch('src.api.batch_api.detect_leak_usecase')
    @patch('src.api.batch_api.Path')
    def test_process_video_with_real_path(self, mock_path, mock_usecase):
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance
        mock_usecase.process_video.return_value = []
        response = client.post("/api/v1/process/video?video_path=data/real_test.mp4")
        assert response.status_code == 200

    @patch('src.api.batch_api.batch_processor')
    @patch('src.api.batch_api.Path')
    def test_batch_process_with_callback(self, mock_path, mock_processor):
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance
        mock_processor.process_directory.return_value = []
        response = client.post(
            "/api/v1/batch/process",
            json={"video_paths": ["video1.mp4", "video2.mp4"], "callback_url": "https://example.com/callback"}
        )
        assert response.status_code == 200

    @patch('src.api.batch_api.detect_leak_usecase')
    @patch('src.api.batch_api.Path')
    def test_process_video_error_handling(self, mock_path, mock_usecase):
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance
        mock_usecase.process_video.side_effect = Exception("Processing error")
        response = client.post("/api/v1/process/video?video_path=data/error.mp4")
        assert response.status_code in [500, 503]

    @patch('src.api.batch_api.Path')
    def test_process_video_not_found(self, mock_path):
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance
        response = client.post("/api/v1/process/video?video_path=data/nonexistent.mp4")
        assert response.status_code in [404, 500]
