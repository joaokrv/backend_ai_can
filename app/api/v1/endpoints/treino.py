# app/api/v1/endpoints/treino.py
# Rotas de sugestão (o coração da aplicação)

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.api.schemas.sugestao import SugestaoCreate
from app.api.schemas.feedback import FeedbackCreate
from app.services.ia_agent import generate_training_plan
from app.services.coleta_dados import salvar_exercicios_e_refeicoes, obter_estatisticas_coleta
from app.database.base import get_db
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Gerar plano de treino personalizado",
    description="Recebe dados do usuário, gera plano com IA e salva no banco de dados"
)
async def obter_sugestao(dados: SugestaoCreate, db: Session = Depends(get_db)):
    try:
        logger.info(
            f"Gerando plano para {dados.nome}: "
            f"{dados.idade}a, {dados.peso}kg, {dados.altura}cm, "
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
        
        stats = salvar_exercicios_e_refeicoes(plano, db)
        
        logger.info(
            f"Dados coletados: {stats['exercicios_salvos']} exercícios, "
            f"{stats['refeicoes_salvas']} refeições"
        )
        
        return {
            "plano": plano,
            "coleta_dados": {
                "exercicios_salvos": stats['exercicios_salvos'],
                "refeicoes_salvas": stats['refeicoes_salvas'],
                "total": stats['total']
            },
            "status": "Plano gerado e dados coletados para treinamento de modelo",
            "mensagem": f"Plano '{plano.get('nome_da_rotina')}' criado para {dados.nome}"
        }
        
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


@router.get(
    "estatisticas",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Obter estatísticas de coleta de dados",
    description="Retorna informações sobre exercícios e refeições coletadas para treinamento"
)
async def obter_stats(db: Session = Depends(get_db)):
    try:
        stats = obter_estatisticas_coleta(db)
        
        return {
            "status": "sucesso",
            "dados": stats,
            "mensagem": f"Total de {stats.get('total_exercicios', 0)} exercícios e "
                       f"{stats.get('total_refeicoes', 0)} refeições coletados"
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao obter estatísticas. Tente novamente."
        )
