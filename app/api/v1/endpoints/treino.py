# app/api/v1/endpoints/treino.py

from fastapi import APIRouter, HTTPException, status, Depends
from app.api.schemas.sugestao import SugestaoCreate
from app.services.ia_agent import generate_training_plan, obter_preferencias_usuario
import logging
from app.api.schemas.plano import PlanoIAResponse
from app.api import deps
from app.database.models.plano import Plano, PlanoDia, PlanoExercicio
from app.database.models.nutricao import PlanoRefeicao
from app.services import coleta_dados

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "",
    response_model=PlanoIAResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Gerar plano de treino personalizado",
    description="Recebe dados do usuário e gera plano de treino com IA",
)
async def obter_sugestao(
    dados: SugestaoCreate,
    current_user: deps.CurrentUser,
    session: deps.SessionDep,
):
    try:
        logger.info(
            f"Gerando plano para {dados.nome}: "
            f"{dados.idade}a, {dados.peso}kg, {dados.altura}cm, "
            f"{dados.disponibilidade}x/sem, {dados.local.value}, {dados.objetivo.value}"
        )
        
        preferencias = obter_preferencias_usuario(current_user.id, session)
        
        if preferencias["exercicios_evitar"] or preferencias["refeicoes_evitar"]:
            logger.info(f"Aplicando preferências do usuário {current_user.id}: "
                       f"{len(preferencias['exercicios_evitar'])} exercícios a evitar, "
                       f"{len(preferencias['refeicoes_evitar'])} refeições a evitar")

        plano_ia = generate_training_plan(
            nome=dados.nome,
            altura=dados.altura,
            peso=dados.peso,
            idade=dados.idade,
            disponibilidade=dados.disponibilidade,
            local=dados.local.value,
            objetivo=dados.objetivo.value,
            preferencias=preferencias, 
        )

        logger.info(f"Plano gerado com sucesso para {dados.nome}")

        try:
            # Criar Plano
            novo_plano = Plano(
                nome=plano_ia.get("nome_da_rotina", "Rotina Personalizada"),
                descricao=f"Rotina gerada por IA para {dados.objetivo.value}",
                usuario_id=current_user.id,
            )
            session.add(novo_plano)
            session.flush()  # Para obter o ID

            # Criar Dias e Exercícios
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

                exercicios = dia_data.get("exercicios", [])
                for j, ex_data in enumerate(exercicios):
                    exercicio = PlanoExercicio(
                        dia_id=dia.id,
                        nome=ex_data.get("nome", "Exercício"),
                        series=ex_data.get("series", ""),
                        repeticoes=ex_data.get("repeticoes", ""),
                        descanso_segundos=ex_data.get("descanso_segundos", 60),
                        detalhes_execucao=ex_data.get("detalhes_execucao", ""),
                        video_url=ex_data.get("video_url", ""),
                        ordem=j + 1,
                    )
                    session.add(exercicio)

            # Criar Refeições do Plano
            nutricao = plano_ia.get("sugestoes_nutricionais", {})
            for tipo in ["pre_treino", "pos_treino"]:
                opcoes = nutricao.get(tipo, {})
                for nivel, refeicao_data in opcoes.items():
                    refeicao = PlanoRefeicao(
                        plano_id=novo_plano.id,
                        nome=refeicao_data.get("nome", f"Opção {nivel}"),
                        custo_estimado=refeicao_data.get("custo_estimado", ""),
                        tipo=tipo,
                        nivel=nivel,
                        ingredientes=refeicao_data.get("ingredientes", []),
                        link_receita=refeicao_data.get("link_receita", ""),
                        explicacao=refeicao_data.get("explicacao", ""),
                    )
                    session.add(refeicao)

            session.commit()
            logger.info(f"Plano salvo no banco com ID: {novo_plano.id}")
            
            # Adicionar ID da rotina na resposta
            plano_ia["rotina_id"] = novo_plano.id
            
            # Coletar dados para Catálogo (Exercícios e Refeições únicos)
            try:
                coleta_dados.salvar_exercicios_e_refeicoes(plano_ia, session)
            except Exception as e:
                logger.error(f"Erro na coleta de dados (não crítico): {e}")

        except Exception as db_err:
            logger.error(f"Erro ao salvar no banco: {db_err}", exc_info=True)
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao salvar rotina no banco de dados.",
            )

        return {
            "plano": plano_ia,
            "status": "sucesso",
            "mensagem": f"Plano '{plano_ia.get('nome_da_rotina')}' criado para {dados.nome}",
        }

    except ValueError as e:
        logger.warning(f"Validação falhou: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar requisição: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar requisição. Tente novamente.",
        )
