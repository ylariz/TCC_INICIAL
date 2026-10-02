from pydantic import BaseModel

class ExecucaoRequest(BaseModel):
    codigo: str
    entrada: str
