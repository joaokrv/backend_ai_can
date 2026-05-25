from fastapi import APIRouter, HTTPException, status, Request, BackgroundTasks
from app.services.ia_agent import generate_training_plan
from app.services.feedback_service import obter_preferencias_para_ia
from app.services.plano_service import persistir_plano_ia
from app.services import coleta_dados
from app.api.schemas.plano import PlanoIAResponse
from app.api import deps
from app.api.utils.db_errors import handle_db_errors
from app.database.base import SessionLocal
from app.core.limiter import limiter
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


def _coletar_em_background(plano_ia: dict):
    """Roda coleta de dados em background com sessao isolada."""
    db = SessionLocal()
    try:
        coleta_dados.salvar_exercicios_e_refeicoes(plano_ia, db)
    finally:
        db.close()


@router.post(
    "",
    response_model=PlanoIAResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Gerar plano de treino personalizado",
)
@limiter.limit("3/hour")
def obter_sugestao(
    request: Request,
    background_tasks: BackgroundTasks,
    current_user: deps.CurrentUser,
    session: deps.SessionDep,
):
    if not current_user.onboarding_completo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Complete seu perfil em PUT /me antes de gerar um plano de treino",
        )

    logger.info(f"Gerando plano: user_id={current_user.id}, objetivo={current_user.objetivo}")

    preferencias = obter_preferencias_para_ia(current_user.id, session)

    try:
        plano_ia = generate_training_plan(user=current_user, preferencias=preferencias)
    except ValueError as e:
        logger.warning(f"Validacao IA falhou: user_id={current_user.id}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    try:
        novo_plano = persistir_plano_ia(plano_ia, current_user, session)
    except Exception as db_err:
        session.rollback()
        logger.error(f"Erro ao salvar plano: user_id={current_user.id}: {db_err}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao salvar rotina no banco de dados.",
        )

    plano_ia["rotina_id"] = novo_plano.id
    background_tasks.add_task(_coletar_em_background, plano_ia)

    return {
        "plano": plano_ia,
        "status": "sucesso",
        "mensagem": f"Plano '{plano_ia.get('nome_da_rotina')}' criado",
    }
