"""
REST API для батчевой обработки видео
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from pathlib import Path
import logging

from src.infrastructure.model_inference import PyTorchModelInference
from src.infrastructure.video_processor import OpenCVVideoProcessor
from src.infrastructure.repository import SQLiteRepository
from src.usecases.detect_leak import DetectLeakUseCase
from src.usecases.batch_process import BatchProcessUseCase
from config.config import config

logging.basicConfig(level=config.log_level)
logger = logging.getLogger(__name__)

app = FastAPI(title="Gas Leak Detection API", version="1.0.0")

# Инициализация зависимостей
model = PyTorchModelInference()
video_processor = OpenCVVideoProcessor()
repository = SQLiteRepository()
detect_leak_usecase = DetectLeakUseCase(
    model=model,
    video_processor=video_processor,
    repository=repository,
    confidence_threshold=config.model.confidence_threshold
)
batch_processor = BatchProcessUseCase(
    detect_leak_usecase=detect_leak_usecase,
    max_workers=4
)

class VideoBatchRequest(BaseModel):
    """Запрос на батчевую обработку"""
    video_paths: List[str]
    callback_url: Optional[str] = None

class BatchStatusResponse(BaseModel):
    """Статус батчевой задачи"""
    job_id: str
    status: str
    total_videos: int
    processed_videos: int
    created_at: datetime
    updated_at: datetime

class DetectionResult(BaseModel):
    """Результат детекции"""
    video_path: str
    leak_probability: float
    is_leak: bool
    timestamp: datetime
    confidence: float

@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/v1/batch/process", response_model=BatchStatusResponse)
async def start_batch_processing(request: VideoBatchRequest, background_tasks: BackgroundTasks):
    """
    Запуск батчевой обработки видео
    
    Args:
        request: Запрос с путями к видео
        background_tasks: Фоновые задачи FastAPI
    
    Returns:
        Статус задачи
    """
    try:
        # Валидация путей
        video_paths = [Path(path) for path in request.video_paths]
        for video_path in video_paths:
            if not video_path.exists():
                raise HTTPException(status_code=404, detail=f"Video not found: {video_path}")
        
        # Запускаем обработку в фоне
        background_tasks.add_task(batch_processor.process_directory, 
                                  Path(request.video_paths[0]).parent, 
                                  Path("./results"))
        
        return BatchStatusResponse(
            job_id="batch_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
            status="started",
            total_videos=len(video_paths),
            processed_videos=0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error starting batch processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/detections", response_model=List[DetectionResult])
async def get_detections(video_path: Optional[str] = None, limit: int = 100):
    """
    Получение результатов детекции
    
    Args:
        video_path: Фильтр по видео (опционально)
        limit: Лимит результатов
    
    Returns:
        Список детекций
    """
    # Здесь нужно реализовать получение из репозитория
    # Пока возвращаем заглушку
    return []

@app.post("/api/v1/process/video")
async def process_single_video(video_path: str, background_tasks: BackgroundTasks):
    """
    Обработка одного видео
    """
    try:
        video_path_obj = Path(video_path)
        if not video_path_obj.exists():
            raise HTTPException(status_code=404, detail=f"Video not found: {video_path}")
        
        background_tasks.add_task(detect_leak_usecase.process_video, video_path_obj)
        
        return {
            "status": "processing",
            "video_path": video_path,
            "message": "Video processing started"
        }
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
