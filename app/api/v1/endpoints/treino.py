# app/api/v1/endpoints/treino.py
# Rotas de sugestão (o coração da aplicação)

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from app.api.schemas.sugestao import SugestaoCreate
from app.api.schemas.feedback import FeedbackCreate
from app.services.ia_agent import generate_training_plan
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/sugestao",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Gerar plano de treino personalizado",
    description="Recebe dados do usuário e retorna plano de treino e dieta gerado por IA"
)
async def obter_sugestao(dados: SugestaoCreate):
    """
    Gera um plano de treino personalizado baseado nos dados do usuário.
    
    **Parâmetros:**
    - **nome**: Nome completo do usuário
    - **altura**: Altura em metros (ex: 1.75)
    - **peso**: Peso em kg (ex: 80)
    - **idade**: Idade em anos (ex: 30)
    - **disponibilidade**: Quantas vezes por semana pode treinar (1-7)
    - **local**: Local de treino (academia, casa, arLivre)
    - **objetivo**: Objetivo principal (perder, ganhar, hipertrofia)
    
    **Retorna:**
    - Plano de treino completo com exercícios detalhados
    - Sugestões nutricionais pré e pós-treino
    
    **Possíveis erros:**
    - 400: Dados inválidos
    - 500: Erro ao processar com IA
    """
    try:
        logger.info(
            f"Gerando plano para {dados.nome}: "
            f"{dados.idade}a, {dados.peso}kg, {dados.altura}m, "
            f"{dados.disponibilidade}x/sem, {dados.local.value}, {dados.objetivo.value}"
        )
        
        plano = generate_training_plan(
            nome=dados.nome,
            altura=dados.altura,
            peso=dados.peso,
            idade=dados.idade,
            disponibilidade=dados.disponibilidade,
            local=dados.local.value,
            objetivo=dados.objetivo.value
        )
        
        logger.info(f"Plano gerado com sucesso para {dados.nome}")
        return plano
        
    except ValueError as e:
        logger.warning(f"Validação falhou: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao processar requisição: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar requisição. Tente novamente."
        )


@router.post(
    "/feedback",
    status_code=status.HTTP_201_CREATED,
    summary="Enviar feedback sobre sugestão"
)
async def enviar_feedback(feedback: FeedbackCreate):
    """
    Endpoint para o usuário enviar feedback sobre a sugestão recebida.
    
    **Nota:** Implementação futura para salvar no banco de dados.
    """
    logger.info(f"Feedback recebido: usuário {feedback.usuario_id}")
    # TODO: Implementar lógica para salvar feedback no banco
    return {"message": "Feedback recebido com sucesso"}
