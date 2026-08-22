import os
from typing import Dict, Any

import torch
from PIL import Image
from torch import nn
from torchvision import models, transforms

from backend.metadata import SPECIES_CLASSES, SPECIES_INDEX

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "marinextract_efficientnetv2.pth")


def build_model(num_classes: int = 7) -> nn.Module:
    model = models.efficientnet_v2_s(weights=None)
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.2),
        nn.Linear(1280, 256),
        nn.ReLU(inplace=True),
        nn.Dropout(p=0.2),
        nn.Linear(256, num_classes),
    )
    return model


class MarineXtractModel:
    def __init__(self, model_path: str = MODEL_PATH):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = build_model(len(SPECIES_CLASSES))
        checkpoint = torch.load(model_path, map_location=self.device)
        self.model.load_state_dict(checkpoint, strict=True)
        self.model.to(self.device)
        self.model.eval()

        self.transform = transforms.Compose(
            [
                transforms.Resize((384, 384)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225],
                ),
            ]
        )

    def predict(self, image: Image.Image) -> Dict[str, Any]:
        processed = self.transform(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            logits = self.model(processed)
            probabilities = torch.softmax(logits, dim=1)
            confidence, index = torch.max(probabilities, dim=1)

        class_id = int(index.item())
        confidence_percent = round(float(confidence.item()) * 100, 2)
        species_info = SPECIES_INDEX[class_id]

        return {
            "species_id": class_id,
            "predicted_species": species_info["species"],
            "common_name": species_info["common_name"],
            "confidence": confidence_percent,
            "commercial_uses": species_info["commercial_uses"],
            "commercial_value_inr": species_info["commercial_value_inr"],
            "price_per_kg_inr": species_info["commercial_value_inr"],
        }


model_service = MarineXtractModel()
