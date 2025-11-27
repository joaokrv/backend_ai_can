# app/services/coleta_dados.py

from sqlalchemy.orm import Session
from app.database.models.catalogo_exercicio import CatalogoExercicio
from app.database.models.nutricao import CatalogoRefeicao
import logging

logger = logging.getLogger(__name__)


def salvar_exercicios_e_refeicoes(plano: dict, db: Session):
    """
    Salva exercícios e refeições únicos nas tabelas de catálogo.
    """
    logger.info("Iniciando coleta de exercícios e refeições para catálogo")
    
    novos_exercicios = 0
    novas_refeicoes = 0

    try:
        # Coletar Exercícios
        dias = plano.get("dias_de_treino", [])
        for dia in dias:
            exercicios = dia.get("exercicios", [])
            for ex in exercicios:
                nome = ex.get("nome")
                if not nome:
                    continue
                
                # Verifica se já existe no catálogo
                existe = db.query(CatalogoExercicio).filter(CatalogoExercicio.nome == nome).first()
                if not existe:
                    novo_ex = CatalogoExercicio(
                        nome=nome,
                        descricao=ex.get("detalhes_execucao"),
                        video_url=ex.get("video_url")
                    )
                    db.add(novo_ex)
                    novos_exercicios += 1

        # Coletar Refeições
        nutricao = plano.get("sugestoes_nutricionais", {})
        for tipo in ["pre_treino", "pos_treino"]:
            opcoes = nutricao.get(tipo, {})
            for nivel, refeicao_data in opcoes.items():
                nome = refeicao_data.get("nome")
                if not nome:
                    continue

                # Verifica se já existe no catálogo
                existe = db.query(CatalogoRefeicao).filter(CatalogoRefeicao.nome == nome).first()
                
                if not existe:
                    nova_ref = CatalogoRefeicao(
                        nome=nome,
                        custo_estimado=refeicao_data.get("custo_estimado"),
                        tipo=tipo,
                        nivel=nivel,
                        ingredientes=refeicao_data.get("ingredientes"),
                        link_receita=refeicao_data.get("link_receita"),
                        explicacao=refeicao_data.get("explicacao")
                    )
                    db.add(nova_ref)
                    novas_refeicoes += 1

        db.commit()
        logger.info(f"Dados coletados! Novos Exercícios: {novos_exercicios}, Novas Refeições: {novas_refeicoes}")

    except Exception as e:
        logger.error(f"Erro ao coletar dados para catálogo: {e}")
