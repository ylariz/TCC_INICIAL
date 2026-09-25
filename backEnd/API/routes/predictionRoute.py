from fastapi import APIRouter
from API.controllers.predictionController import pergunta
from API.models.predicitionModel import PredictionRequest

router = APIRouter()

@router.post("/pergunta")
def post_prediction(request: PredictionRequest):
    return pergunta(request)