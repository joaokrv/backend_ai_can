"""
Serviço para coletar e armazenar dados de exercícios e refeições retornados pela IA.

Estes dados serão usados para treinar modelos de ML futuramente.
"""

from sqlalchemy.orm import Session
from app.database.models.exercicio import Exercicio
from app.database.models.refeicoes import Refeicao
from typing import Dict, Any, List
import logging
import json

logger = logging.getLogger(__name__)


def salvar_exercicios_e_refeicoes(plano: Dict[str, Any], db: Session) -> Dict[str, Any]:
    try:
        exercicios_salvos = 0
        refeicoes_salvas = 0

        logger.info("Iniciando coleta de exercícios e refeições para base de dados")

        exercicios_salvos = _salvar_exercicios(plano, db)
        refeicoes_salvas = _salvar_refeicoes(plano, db)

        db.commit()

        stats = {
            "exercicios_salvos": exercicios_salvos,
            "refeicoes_salvas": refeicoes_salvas,
            "total": exercicios_salvos + refeicoes_salvas,
        }

        logger.info(
            f"Dados coletados com sucesso! "
            f"Exercícios: {exercicios_salvos}, "
            f"Refeições: {refeicoes_salvas}"
        )

        return stats

    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao coletar dados: {e}", exc_info=True)
        raise


def _salvar_exercicios(plano: Dict[str, Any], db: Session) -> int:
    contador = 0
    dias_treino = plano.get("dias_de_treino", [])

    for dia_info in dias_treino:
        exercicios_dia = dia_info.get("exercicios", [])

        for exercicio_info in exercicios_dia:

            nome = exercicio_info.get("nome", "").strip()

            exercicio_existente = (
                db.query(Exercicio).filter(Exercicio.nome == nome).first()
            )

            if exercicio_existente:
                logger.debug(f"Exercício '{nome}' já existe no banco, pulando...")
                continue

            exercicio = Exercicio(
                nome=nome,
                descricao=exercicio_info.get("detalhes_execucao", ""),
                tipo="treino",
                nivel="intermediário",
                video_url=exercicio_info.get("video_url", ""),
            )

            db.add(exercicio)
            contador += 1

            logger.debug(
                f"Exercício '{nome}' adicionado para coleta "
                f"(Series: {exercicio_info.get('series')}, "
                f"Repetições: {exercicio_info.get('repeticoes')})"
            )

    db.flush()
    return contador


def _salvar_refeicoes(plano: Dict[str, Any], db: Session) -> int:
    contador = 0
    sugestoes_nut = plano.get("sugestoes_nutricionais", {})

    tipos_refeicao = {"pre_treino": "pre_treino", "pos_treino": "pos_treino"}

    for tipo_key, tipo_label in tipos_refeicao.items():
        opcoes = sugestoes_nut.get(tipo_key, {})

        niveis_map = {
            "opcao_economica": "economica",
            "economica": "economica",
            "opcao_equilibrada": "equilibrada",
            "equilibrada": "equilibrada",
            "opcao_premium": "premium",
            "premium": "premium",
        }

        for chave_original, refeicao_info in opcoes.items():

            nome = refeicao_info.get("nome", "").strip()

            if not nome:
                continue

            refeicao_existente = (
                db.query(Refeicao).filter(Refeicao.nome == nome).first()
            )

            if refeicao_existente:
                logger.debug(f"Refeição '{nome}' já existe no banco, pulando...")
                continue

            nivel = niveis_map.get(chave_original, "não-classificado")

            refeicao = Refeicao(
                nome=nome,
                custo_estimado=refeicao_info.get("custo_estimado", ""),
                tipo=tipo_label,  # "pre_treino" ou "pos_treino"
                nivel=nivel,  # "economica", "equilibrada", "premium"
                ingredientes=refeicao_info.get("ingredientes", []),
                link_receita=refeicao_info.get("link_receita", ""),
                explicacao=refeicao_info.get("explicacao", ""),
                rotina_id=None,  # Sem relação com rotina/usuário
            )

            db.add(refeicao)
            contador += 1

            logger.debug(
                f"Refeição '{nome}' ({tipo_label} - {nivel}) adicionada para coleta"
            )

    db.flush()
    return contador


def obter_estatisticas_coleta(db: Session) -> Dict[str, Any]:
    try:
        total_exercicios = db.query(Exercicio).count()

        total_refeicoes = (
            db.query(Refeicao).filter(Refeicao.rotina_id.is_(None)).count()
        )

        # Agrupar por tipo
        pre_treino = (
            db.query(Refeicao)
            .filter(Refeicao.tipo == "pre_treino", Refeicao.rotina_id.is_(None))
            .count()
        )

        pos_treino = (
            db.query(Refeicao)
            .filter(Refeicao.tipo == "pos_treino", Refeicao.rotina_id.is_(None))
            .count()
        )

        # Agrupar por nível
        economica = (
            db.query(Refeicao)
            .filter(Refeicao.nivel == "economica", Refeicao.rotina_id.is_(None))
            .count()
        )

        equilibrada = (
            db.query(Refeicao)
            .filter(Refeicao.nivel == "equilibrada", Refeicao.rotina_id.is_(None))
            .count()
        )

        premium = (
            db.query(Refeicao)
            .filter(Refeicao.nivel == "premium", Refeicao.rotina_id.is_(None))
            .count()
        )

        return {
            "total_exercicios": total_exercicios,
            "total_refeicoes": total_refeicoes,
            "refeicoes_por_tipo": {"pre_treino": pre_treino, "pos_treino": pos_treino},
            "refeicoes_por_nivel": {
                "economica": economica,
                "equilibrada": equilibrada,
                "premium": premium,
            },
        }

    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        return {}
