from pydantic import BaseModel
from typing import List, Dict

class Ingredient(BaseModel):
    name: str
    confidence: float = 0.0

class Assessment(BaseModel):
    rating: str
    reason: str

class AnalysisResult(BaseModel):
    assessments: Dict[str, Assessment]
