import pytest
from pathlib import Path
from PIL import Image
import torch

from src.infrastructure.model_inference import PyTorchModelInference

class TestPyTorchModelInference:
    
    def test_model_initialization(self):
        """Тест инициализации модели"""
        model = PyTorchModelInference()
        assert model is not None
        assert model.device is not None
    
    def test_predict_returns_dict(self):
        """Тест метода predict"""
        model = PyTorchModelInference()
        img = Image.new('RGB', (224, 224), color='red')
        result = model.predict(img)
        
        assert 'leak_probability' in result
        assert 'is_leak' in result
        assert 'confidence' in result
        assert isinstance(result['leak_probability'], float)
        assert isinstance(result['is_leak'], bool)
    
    def test_predict_batch(self):
        """Тест батчевого предсказания"""
        model = PyTorchModelInference()
        images = [Image.new('RGB', (224, 224), color='red') for _ in range(3)]
        results = model.predict_batch(images)
        
        assert len(results) == 3
        for result in results:
            assert 'leak_probability' in result
            assert 'is_leak' in result
