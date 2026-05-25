from sqlalchemy.orm import Session
from app.database.models.feedback import Feedback
from app.api.schemas.enums import TipoFeedback
import logging

logger = logging.getLogger(__name__)

MAX_PREFERENCIAS_POR_CATEGORIA = 50


def agrupar_feedbacks(user_id: int, session: Session, limite_por_categoria: int = MAX_PREFERENCIAS_POR_CATEGORIA) -> dict:
    """Retorna dict com 4 listas (exercicios/refeicoes x gostou/nao_gostou).
    Limita cada lista a `limite_por_categoria` itens mais recentes (defesa contra OOM)."""
    rows = (
        session.query(Feedback.tipo, Feedback.gostou, Feedback.item_nome)
        .filter(Feedback.usuario_id == user_id)
        .order_by(Feedback.created_at.desc())
        .limit(limite_por_categoria * 4)
        .all()
    )

    resultado = {
        "exercicios_gostou": [],
        "exercicios_nao_gostou": [],
        "refeicoes_gostou": [],
        "refeicoes_nao_gostou": [],
    }

    for tipo, gostou, nome in rows:
        if tipo == TipoFeedback.EXERCICIO.value:
            chave = "exercicios_gostou" if gostou else "exercicios_nao_gostou"
        elif tipo == TipoFeedback.REFEICAO.value:
            chave = "refeicoes_gostou" if gostou else "refeicoes_nao_gostou"
        else:
            continue
        if len(resultado[chave]) < limite_por_categoria:
            resultado[chave].append(nome)

    return resultado


def obter_preferencias_para_ia(user_id: int, session: Session) -> dict:
    """Formato esperado pelo ia_agent: chaves preferidos/evitar."""
    base = agrupar_feedbacks(user_id, session, limite_por_categoria=10)
    return {
        "exercicios_preferidos": base["exercicios_gostou"],
        "exercicios_evitar": base["exercicios_nao_gostou"],
        "refeicoes_preferidas": base["refeicoes_gostou"],
        "refeicoes_evitar": base["refeicoes_nao_gostou"],
    }
