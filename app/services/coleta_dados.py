from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.database.models.catalogo_exercicio import CatalogoExercicio
from app.database.models.nutricao import CatalogoRefeicao
import logging

logger = logging.getLogger(__name__)


def salvar_exercicios_e_refeicoes(plano: dict, db: Session):
    """Salva exercicios e refeicoes unicos no catalogo via INSERT ... ON CONFLICT DO NOTHING.
    1 query por categoria em vez de N+1 SELECTs + N INSERTs."""
    try:
        exercicios = []
        nomes_ex_vistos = set()
        for dia in plano.get("dias_de_treino", []):
            for ex in dia.get("exercicios", []):
                nome = ex.get("nome")
                if not nome or nome in nomes_ex_vistos:
                    continue
                nomes_ex_vistos.add(nome)
                exercicios.append({
                    "nome": nome,
                    "descricao": ex.get("detalhes_execucao"),
                    "video_url": ex.get("video_url"),
                })

        refeicoes = []
        nomes_ref_vistos = set()
        for tipo in ["pre_treino", "pos_treino"]:
            for nivel, ref_data in plano.get("sugestoes_nutricionais", {}).get(tipo, {}).items():
                nome = ref_data.get("nome")
                if not nome or nome in nomes_ref_vistos:
                    continue
                nomes_ref_vistos.add(nome)
                refeicoes.append({
                    "nome": nome,
                    "custo_estimado": ref_data.get("custo_estimado"),
                    "tipo": tipo,
                    "nivel": nivel,
                    "ingredientes": ref_data.get("ingredientes"),
                    "link_receita": ref_data.get("link_receita"),
                    "explicacao": ref_data.get("explicacao"),
                })

        if exercicios:
            stmt = pg_insert(CatalogoExercicio).values(exercicios).on_conflict_do_nothing(index_elements=["nome"])
            db.execute(stmt)
        if refeicoes:
            stmt = pg_insert(CatalogoRefeicao).values(refeicoes).on_conflict_do_nothing(index_elements=["nome"])
            db.execute(stmt)

        db.commit()
        logger.info(f"Coleta concluida: {len(exercicios)} exercicios, {len(refeicoes)} refeicoes (incluindo duplicatas ignoradas)")

    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao coletar dados para catalogo: {e}")
