import traceback

from fastapi import APIRouter, UploadFile, File, HTTPException

from informed_be.workflows.ingredient_graph import analyze_ingredients
from informed_be.models.schemas import AnalysisResult

router = APIRouter()

@router.post("/analyze", response_model=AnalysisResult)
async def analyze_image(file: UploadFile = File(...)) -> AnalysisResult:
    try:
        image_bytes = await file.read()

        if not image_bytes:
            raise HTTPException(status_code=400, detail="Empty file received")

        return analyze_ingredients(image_bytes)
    except HTTPException as he:
        raise he
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
