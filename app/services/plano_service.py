from sqlalchemy.orm import Session, selectinload
from fastapi import HTTPException, status
from app.database.models.plano import Plano, PlanoDia, PlanoExercicio
from app.database.models.nutricao import PlanoRefeicao
from app.database.models.user import User
from app.api.schemas.enums import StatusPlano
import logging

logger = logging.getLogger(__name__)


def get_plano_or_403(plano_id: int, user_id: int, session: Session) -> Plano:
    """Busca plano com IDOR check. 404 se nao existe, 403 se nao pertence ao user."""
    plano = session.query(Plano).filter(Plano.id == plano_id, Plano.usuario_id == user_id).first()
    if not plano:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plano nao encontrado")
    return plano


def get_plano_detalhado_or_403(plano_id: int, user_id: int, session: Session) -> Plano:
    """Igual a get_plano_or_403 mas com eager loading de dias/exercicios/refeicoes."""
    plano = (
        session.query(Plano)
        .options(
            selectinload(Plano.dias).selectinload(PlanoDia.exercicios),
            selectinload(Plano.refeicoes),
        )
        .filter(Plano.id == plano_id, Plano.usuario_id == user_id)
        .first()
    )
    if not plano:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plano nao encontrado")
    return plano


def persistir_plano_ia(plano_ia: dict, user: User, session: Session) -> Plano:
    """Persiste plano gerado pela IA atomicamente: arquiva anteriores + cria novo em 1 transacao."""
    session.query(Plano).filter(
        Plano.usuario_id == user.id,
        Plano.status == StatusPlano.ATIVO.value,
    ).update({"status": StatusPlano.ARQUIVADO.value}, synchronize_session=False)

    novo_plano = Plano(
        nome=plano_ia.get("nome_da_rotina", "Rotina Personalizada"),
        descricao=f"Rotina gerada por IA para {user.objetivo}",
        usuario_id=user.id,
        explicacao_ia=plano_ia.get("explicacao_ia"),
    )
    session.add(novo_plano)
    session.flush()

    dias_treino = plano_ia.get("dias_de_treino", [])
    for i, dia_data in enumerate(dias_treino):
        dia = PlanoDia(
            plano_id=novo_plano.id,
            identificacao=dia_data.get("identificacao", f"Dia {i+1}"),
            foco_muscular=dia_data.get("foco_muscular", ""),
            ordem=i + 1,
        )
        session.add(dia)
        session.flush()

        exercicios = [
            PlanoExercicio(
                dia_id=dia.id,
                nome=ex.get("nome", "Exercicio"),
                series=ex.get("series", ""),
                repeticoes=ex.get("repeticoes", ""),
                descanso_segundos=ex.get("descanso_segundos", 60),
                detalhes_execucao=ex.get("detalhes_execucao", ""),
                video_url=ex.get("video_url", ""),
                ordem=j + 1,
            )
            for j, ex in enumerate(dia_data.get("exercicios", []))
        ]
        session.add_all(exercicios)

    nutricao = plano_ia.get("sugestoes_nutricionais", {})
    refeicoes = []
    for tipo in ["pre_treino", "pos_treino"]:
        for nivel, ref_data in nutricao.get(tipo, {}).items():
            refeicoes.append(PlanoRefeicao(
                plano_id=novo_plano.id,
                nome=ref_data.get("nome", f"Opcao {nivel}"),
                custo_estimado=ref_data.get("custo_estimado", ""),
                tipo=tipo,
                nivel=nivel,
                ingredientes=ref_data.get("ingredientes", []),
                link_receita=ref_data.get("link_receita", ""),
                explicacao=ref_data.get("explicacao", ""),
                calorias=ref_data.get("calorias"),
                proteina_g=ref_data.get("proteina_g"),
                carboidrato_g=ref_data.get("carboidrato_g"),
                gordura_g=ref_data.get("gordura_g"),
                macros_estimados=True,
            ))
    session.add_all(refeicoes)

    session.commit()
    logger.info(f"Plano persistido: plano_id={novo_plano.id}, user_id={user.id}")
    return novo_plano