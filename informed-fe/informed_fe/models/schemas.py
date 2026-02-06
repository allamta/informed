from pydantic import BaseModel
from typing import List, Dict

class Assessment(BaseModel):
    rating: str
    reason: str

class AnalysisResult(BaseModel):
    assessments: Dict[str, Assessment]
