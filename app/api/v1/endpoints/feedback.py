# app/api/v1/endpoints/feedback.py
"""Endpoints para sistema de feedback de exercícios e refeições."""

from fastapi import APIRouter, status, HTTPException
from sqlalchemy import func, desc
from app.api import deps
from app.api.schemas.feedback import (
    FeedbackCreate,
    FeedbackResponse,
    PreferenciasUsuario,
    FeedbackStats
)
from app.database.models.feedback import Feedback
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/exercicio",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Avaliar exercício",
    description="Salva feedback positivo ou negativo de um exercício"
)
async def criar_feedback_exercicio(
    feedback: FeedbackCreate,
    current_user: deps.CurrentUser,
    session: deps.SessionDep,
):
    """
    Salva avaliação de exercício (gostei/não gostei).
    
    O sistema usa esse feedback para personalizar futuros planos de treino.
    """
    try:
        db_feedback = Feedback(
            usuario_id=current_user.id,
            tipo="exercicio",
            item_nome=feedback.item_nome,
            gostou=feedback.gostou,
            comentario=feedback.comentario
        )
        
        session.add(db_feedback)
        session.commit()
        session.refresh(db_feedback)
        
        logger.info(f"Feedback de exercício salvo: usuário={current_user.id}, "
                   f"item={feedback.item_nome}, gostou={feedback.gostou}")
        
        return db_feedback
        
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao salvar feedback de exercício: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao salvar feedback"
        )


@router.post(
    "/refeicao",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Avaliar refeição",
    description="Salva feedback positivo ou negativo de uma refeição/ingrediente"
)
async def criar_feedback_refeicao(
    feedback: FeedbackCreate,
    current_user: deps.CurrentUser,
    session: deps.SessionDep,
):
    """
    Salva avaliação de refeição (gostei/não gostei).
    
    O sistema evita sugerir refeições/ingredientes que o usuário não gosta.
    """
    try:
        db_feedback = Feedback(
            usuario_id=current_user.id,
            tipo="refeicao",
            item_nome=feedback.item_nome,
            gostou=feedback.gostou,
            comentario=feedback.comentario
        )
        
        session.add(db_feedback)
        session.commit()
        session.refresh(db_feedback)
        
        logger.info(f"Feedback de refeição salvo: usuário={current_user.id}, "
                   f"item={feedback.item_nome}, gostou={feedback.gostou}")
        
        return db_feedback
        
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao salvar feedback de refeição: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao salvar feedback"
        )


@router.get(
    "/me",
    response_model=PreferenciasUsuario,
    summary="Listar minhas preferências",
    description="Retorna agregado de exercícios e refeições que o usuário gostou/não gostou"
)
async def listar_preferencias(
    current_user: deps.CurrentUser,
    session: deps.SessionDep,
):
    """
    Lista todas as preferências do usuário organizadas por tipo.
    
    Útil para o usuário revisar seus feedbacks e para debug.
    """
    try:
        feedbacks = session.query(Feedback).filter(
            Feedback.usuario_id == current_user.id
        ).all()
        
        preferencias = PreferenciasUsuario()
        
        for feedback in feedbacks:
            if feedback.tipo == "exercicio":
                if feedback.gostou:
                    preferencias.exercicios["gostou"].append(feedback.item_nome)
                else:
                    preferencias.exercicios["nao_gostou"].append(feedback.item_nome)
            elif feedback.tipo == "refeicao":
                if feedback.gostou:
                    preferencias.refeicoes["gostou"].append(feedback.item_nome)
                else:
                    preferencias.refeicoes["nao_gostou"].append(feedback.item_nome)
        
        return preferencias
        
    except Exception as e:
        logger.error(f"Erro ao listar preferências: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar preferências"
        )


@router.delete(
    "/{feedback_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar feedback",
    description="Remove um feedback específico (apenas do próprio usuário)"
)
async def deletar_feedback(
    feedback_id: int,
    current_user: deps.CurrentUser,
    session: deps.SessionDep,
):
    """
    Deleta um feedback.
    
    Útil se o usuário mudou de opinião sobre um item.
    """
    try:
        feedback = session.query(Feedback).filter(
            Feedback.id == feedback_id,
            Feedback.usuario_id == current_user.id  # Segurança: só pode deletar próprio feedback
        ).first()
        
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback não encontrado"
            )
        
        session.delete(feedback)
        session.commit()
        
        logger.info(f"Feedback deletado: id={feedback_id}, usuário={current_user.id}")
        
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao deletar feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao deletar feedback"
        )


@router.get(
    "/stats",
    response_model=FeedbackStats,
    summary="Estatísticas de feedback",
    description="Retorna métricas agregadas (taxa de satisfação, itens mais rejeitados)"
)
async def obter_estatisticas(
    current_user: deps.CurrentUser,
    session: deps.SessionDep,
):
    """
    Estatísticas de feedback do usuário.
    
    Útil para análise acadêmica e visualização de dados.
    """
    try:
        feedbacks = session.query(Feedback).filter(
            Feedback.usuario_id == current_user.id
        ).all()
        
        total = len(feedbacks)
        positivos = sum(1 for f in feedbacks if f.gostou)
        negativos = total - positivos
        
        taxa_satisfacao = (positivos / total * 100) if total > 0 else 0.0
        
        # Exercícios mais rejeitados
        exercicios_rejeitados = session.query(
            Feedback.item_nome,
            func.count(Feedback.id).label('count')
        ).filter(
            Feedback.usuario_id == current_user.id,
            Feedback.tipo == "exercicio",
            Feedback.gostou == False
        ).group_by(
            Feedback.item_nome
        ).order_by(
            desc('count')
        ).limit(5).all()
        
        # Refeições mais rejeitadas
        refeicoes_rejeitadas = session.query(
            Feedback.item_nome,
            func.count(Feedback.id).label('count')
        ).filter(
            Feedback.usuario_id == current_user.id,
            Feedback.tipo == "refeicao",
            Feedback.gostou == False
        ).group_by(
            Feedback.item_nome
        ).order_by(
            desc('count')
        ).limit(5).all()
        
        return FeedbackStats(
            total_feedbacks=total,
            total_positivos=positivos,
            total_negativos=negativos,
            taxa_satisfacao=round(taxa_satisfacao, 2),
            exercicios_mais_rejeitados=[item[0] for item in exercicios_rejeitados],
            refeicoes_mais_rejeitadas=[item[0] for item in refeicoes_rejeitadas]
        )
        
    except Exception as e:
        logger.error(f"Erro ao gerar estatísticas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao gerar estatísticas"
        )
