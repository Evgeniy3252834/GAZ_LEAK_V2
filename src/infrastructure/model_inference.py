import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
from typing import List, Dict
import logging
from pathlib import Path

from src.domain.interfaces import ModelInferenceInterface
from config.config import config

logger = logging.getLogger(__name__)

class ThermalLeakDetector(nn.Module):
    def __init__(self, num_classes: int = 2):
        super().__init__()
        self.model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        num_features = self.model.fc.in_features
        self.model.fc = nn.Linear(num_features, num_classes)
    
    def forward(self, x):
        return self.model(x)

class PyTorchModelInference(ModelInferenceInterface):
    def __init__(self, model_path: str = None):
        self.device = torch.device(config.model.device)
        self.model = ThermalLeakDetector()
        
        model_path = model_path or config.model.model_path
        if Path(model_path).exists():
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            logger.info(f"Model loaded from {model_path}")
        else:
            logger.warning(f"Model not found at {model_path}, using random weights")
        
        self.model.to(self.device)
        self.model.eval()
        
        self.transform = transforms.Compose([
            transforms.Resize(config.model.image_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    
    def predict(self, image: Image.Image) -> Dict:
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = torch.softmax(outputs, dim=1)
        
        leak_prob = probabilities[0, 1].item()
        
        return {
            'leak_probability': leak_prob,
            'is_leak': leak_prob > config.model.confidence_threshold,
            'confidence': max(leak_prob, 1 - leak_prob)
        }
    
    def predict_batch(self, images: List[Image.Image]) -> List[Dict]:
        batch = []
        for image in images:
            if image.mode != 'RGB':
                image = image.convert('RGB')
            batch.append(self.transform(image))
        
        batch_tensor = torch.stack(batch).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(batch_tensor)
            probabilities = torch.softmax(outputs, dim=1)
        
        results = []
        for prob in probabilities:
            leak_prob = prob[1].item()
            results.append({
                'leak_probability': leak_prob,
                'is_leak': leak_prob > config.model.confidence_threshold,
                'confidence': max(leak_prob, 1 - leak_prob)
            })
        
        return results
