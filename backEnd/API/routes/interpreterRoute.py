from fastapi import APIRouter
from API.models.interpreterModel import ExecucaoRequest
from API.controllers.interpreterController import executar

router = APIRouter()

@router.post("/execute")
def post_interpreter(request: ExecucaoRequest):
    return executar(request)
