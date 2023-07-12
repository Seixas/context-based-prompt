from pydantic import BaseModel
from typing import Optional


class ModelResults(BaseModel):
    """
    Identificador do evento;
    Classificação do evento por valor:
        1 para evento Correto;
        0 para evento Incorreto;
        99 para evento Não Solucionado/Erro.
    Número de iterações do algoritmo para classificação do evento;
    Métricas da classificação;
    """
    video_path: str
    event_id: int
    event_classification: int
    model: str
    iteractions: Optional[int] = None
    metrics: dict
