import os
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

@dataclass(frozen=True)
class ModelConfig:
    """Конфигурация модели"""
    model_path: str = "models/thermal_model.pth"
    device: str = "cuda" if os.getenv("USE_GPU", "false").lower() == "true" else "cpu"
    confidence_threshold: float = 0.5
    image_size: tuple = (224, 224)
    batch_size: int = 32

@dataclass(frozen=True)
class DroneConfig:
    """Конфигурация дрона"""
    descent_height: float = 5.0
    gas_analyzer_timeout: int = 30
    confirmation_retries: int = 3

@dataclass(frozen=True)
class BatchConfig:
    """Конфигурация батчевой обработки"""
    input_bucket: str = "gas-leak-videos"
    output_bucket: str = "gas-leak-results"
    processing_interval: int = 300
    max_video_size_mb: int = 500
    supported_formats: tuple = (".mp4", ".avi", ".mov")

class Config:
    """Главный конфиг проекта"""
    def __init__(self):
        self.env = os.getenv("ENVIRONMENT", "development")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # Загрузка .env
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)
        
        # Подконфиги
        self.model = ModelConfig()
        self.drone = DroneConfig()
        self.batch = BatchConfig()
        
        # Пути
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "data"
        self.results_dir = self.base_dir / "results"
        self.logs_dir = self.base_dir / "logs"
        
        # Создаем директории
        for dir_path in [self.data_dir, self.results_dir, self.logs_dir]:
            dir_path.mkdir(exist_ok=True)
    
    def get_database_url(self) -> str:
        return os.getenv("DATABASE_URL", "sqlite:///./gas_leak.db")

# Singleton
config = Config()
