from google.genai import types
from google.genai.client import Client as GeminiClient
from app.core.config import settings
from app.core.sanitizers import safe_nome, safe_item_nome, safe_lesoes
from app.core.gemini_quota import gemini_quota
from app.api.schemas.enums import OBJETIVO_LABELS, LOCAL_LABELS, ObjetivoTreino, LocalTreino
from string import Template
import re
from urllib.parse import quote_plus
import logging
import json
from typing import Dict, Any, Optional, List
from tenacity import retry, stop_after_attempt, wait_exponential
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ExercicioIA(BaseModel):
    nome: str
    series: str
    repeticoes: str
    descanso_segundos: int
    detalhes_execucao: str
    video_url: Optional[str] = None


class DiaTreinoIA(BaseModel):
    identificacao: str
    foco_muscular: str
    exercicios: List[ExercicioIA]


class RefeicaoIA(BaseModel):
    nome: str
    custo_estimado: str
    ingredientes: List[str]
    link_receita: Optional[str] = None
    explicacao: str
    calorias: int
    proteina_g: float
    carboidrato_g: float
    gordura_g: float


class TimingNutricionalIA(BaseModel):
    opcao_1: RefeicaoIA
    opcao_2: RefeicaoIA


class SugestoesNutricionaisIA(BaseModel):
    pre_treino: TimingNutricionalIA
    pos_treino: TimingNutricionalIA


class PlanoIAResponseSchema(BaseModel):
    explicacao_ia: str
    nome_da_rotina: str
    dias_de_treino: List[DiaTreinoIA]
    sugestoes_nutricionais: SugestoesNutricionaisIA

_gemini_client = None


def get_gemini_client() -> GeminiClient:
    global _gemini_client
    if _gemini_client is None:
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY nao configurada.")
        _gemini_client = GeminiClient(api_key=api_key)
        logger.info("Cliente Gemini inicializado")
    return _gemini_client


def _build_search_url(query: str, target: str) -> str:
    encoded = quote_plus(query)
    if target == "youtube":
        return f"https://www.youtube.com/results?search_query={encoded}"
    return f"https://www.google.com/search?q={encoded}"


def _ensure_search_url(url: Optional[str], query: str, target: str) -> str:
    if not url:
        return _build_search_url(query, target)
    if target == "youtube" and re.search(r"youtube\.com/results\?search_query=", url):
        return url
    if target == "google" and re.search(r"google\.com/search\?q=", url):
        return url
    return _build_search_url(query, target)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), reraise=True)
def _call_gemini_api(prompt: str, response_schema: Optional[type] = None) -> str:
    """Chama Gemini. Quota deve ser verificada antes (fora do retry)."""
    try:
        client = get_gemini_client()
        config_args = {
            "temperature": 0.5,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json",
        }
        if response_schema:
            config_args["response_schema"] = response_schema
            
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(**config_args),
        )
        return response.text
    except Exception as e:
        logger.error(f"Erro Gemini: {e}")
        if "429" in str(e):
            raise ValueError("Servico de IA sobrecarregado. Tente novamente em alguns instantes.")
        if "500" in str(e) or "503" in str(e):
            raise ValueError("Servico de IA indisponivel no momento.")
        raise ValueError(f"Erro na comunicacao com IA: {str(e)}")


def _sanitize_preference_list(items: list) -> str:
    sanitized = []
    for item in items[:10]:
        try:
            sanitized.append(safe_item_nome(item))
        except ValueError:
            continue
    return ", ".join(sanitized)


def _build_prompt(user, preferencias: Optional[dict]) -> str:
    try:
        nome = safe_nome(user.nome, field_name="nome")
    except ValueError:
        nome = f"Usuario {user.idade}"

    altura_metros = user.altura / 100
    imc = user.peso / (altura_metros ** 2)

    try:
        local_descricao = LOCAL_LABELS[LocalTreino(user.local_treino)]
    except (ValueError, KeyError):
        local_descricao = "Local nao especificado"
    try:
        objetivo_descricao = OBJETIVO_LABELS[ObjetivoTreino(user.objetivo)]
    except (ValueError, KeyError):
        objetivo_descricao = "Objetivo nao especificado"

    sexo_descricao = user.sexo or "Nao especificado"
    _VALID_DIA = re.compile(r"^[A-Za-z]{3,15}$")
    dias_sanitizados = [d for d in (user.dias_disponiveis or []) if _VALID_DIA.match(str(d))]
    dias_str = ", ".join(dias_sanitizados) if dias_sanitizados else "Nao informado"
    duracao_str = f"{user.duracao_sessao} minutos" if user.duracao_sessao else "Nao especificado"
    nivel_str = user.nivel_experiencia or "Iniciante"
    num_dias = len(dias_sanitizados) if dias_sanitizados else 3

    restricoes_text = ""
    if user.restricoes_alimentares:
        restricoes_text = f"RESTRICOES ALIMENTARES OBRIGATORIAS: {', '.join(user.restricoes_alimentares)}\nJAMAIS inclua alimentos que violem estas restricoes.\n"

    if user.lesoes_cuidados:
        try:
            lesoes = safe_lesoes(user.lesoes_cuidados)
            if lesoes and lesoes.strip():
                restricoes_text += f"RESTRICAO MEDICA: {lesoes}\nEvite exercicios que agravam isto.\n"
        except Exception:
            pass

    preferencias_text = ""
    if preferencias:
        if preferencias.get("exercicios_evitar"):
            evitar = _sanitize_preference_list(preferencias["exercicios_evitar"])
            if evitar:
                preferencias_text += f"\nEXERCICIOS PROIBIDOS: {evitar}\nSubstituir por alternativas.\n"
        if preferencias.get("refeicoes_evitar"):
            evitar = _sanitize_preference_list(preferencias["refeicoes_evitar"])
            if evitar:
                preferencias_text += f"\nREFEICOES PROIBIDAS: {evitar}\nSugira alternativas diferentes.\n"

    template = Template("""Voce eh uma API. Retorne APENAS JSON valido, sem texto extra.

DADOS DO USUARIO:
Nome: $NOME | Sexo: $SEXO | Altura: $ALTURA cm | Peso: $PESO kg | Idade: $IDADE anos
IMC: $IMC | Nivel: $NIVEL_EXP
Dias disponiveis: $DIAS_DISPONIVEIS | Duracao sessao: $DURACAO_SESSAO
Local: $LOCAL | Objetivo: $OBJETIVO

OBRIGACOES:
1. Retorne JSON com: explicacao_ia, nome_da_rotina, dias_de_treino, sugestoes_nutricionais
2. explicacao_ia (OBRIGATORIO): texto de 150-200 palavras justificando divisao de treino, escolha de exercicios e logica nutricional
3. Gere EXATAMENTE $NUM_DIAS dias de treino
4. Cada exercicio: nome, series (texto), repeticoes (texto), descanso_segundos (numero), detalhes_execucao, video_url
5. CADA REFEICAO DEVE TER: nome, custo_estimado, ingredientes, link_receita, explicacao, calorias (numero inteiro), proteina_g (float), carboidrato_g (float), gordura_g (float)
6. JSON 100% valido - verificar todas virgulas e chaves

$RESTRICOES
$PREFERENCIAS

Exemplo de uma refeicao:
{"nome": "Frango com batata doce", "custo_estimado": "R$$ 7,00", "ingredientes": ["150g frango", "200g batata doce"], "link_receita": "url", "explicacao": "Proteina e carbs", "calorias": 480, "proteina_g": 42.0, "carboidrato_g": 52.0, "gordura_g": 6.0}

{ COMECE AQUI E TERMINE COM } - NADA MAIS!""")

    return template.substitute(
        NOME=nome,
        SEXO=sexo_descricao,
        ALTURA=user.altura,
        PESO=user.peso,
        IDADE=user.idade,
        IMC=f"{imc:.2f}",
        NIVEL_EXP=nivel_str,
        DIAS_DISPONIVEIS=dias_str,
        DURACAO_SESSAO=duracao_str,
        NUM_DIAS=num_dias,
        LOCAL=local_descricao,
        OBJETIVO=objetivo_descricao,
        RESTRICOES=restricoes_text,
        PREFERENCIAS=preferencias_text,
    )


def _normalize_plano(plano: dict) -> dict:
    """Garante tipos corretos em descanso_segundos, video_url, link_receita, macros."""
    for dia in plano.get("dias_de_treino", []):
        for ex in dia.get("exercicios", []):
            descanso = ex.get("descanso_segundos")
            if isinstance(descanso, str) and descanso.isdigit():
                ex["descanso_segundos"] = int(descanso)
            elif not isinstance(descanso, int):
                ex["descanso_segundos"] = 60
            ex["video_url"] = _ensure_search_url(ex.get("video_url"), ex.get("nome", ""), "youtube")

    for timing in ("pre_treino", "pos_treino"):
        block = plano.get("sugestoes_nutricionais", {}).get(timing, {})
        for key, meal in list(block.items()):
            meal["link_receita"] = _ensure_search_url(meal.get("link_receita"), meal.get("nome") or key, "google")
            for field in ["calorias", "proteina_g", "carboidrato_g", "gordura_g"]:
                if field not in meal or meal[field] is None:
                    meal[field] = 0 if field == "calorias" else 0.0
                else:
                    try:
                        meal[field] = int(meal[field]) if field == "calorias" else float(meal[field])
                    except (ValueError, TypeError):
                        meal[field] = 0 if field == "calorias" else 0.0
    return plano


def _validate_plano(plano: dict) -> None:
    if not isinstance(plano, dict):
        raise ValueError("Resposta da IA nao eh um objeto JSON valido")
    if "nome_da_rotina" not in plano:
        raise ValueError("Campo obrigatorio 'nome_da_rotina' ausente")
    if "dias_de_treino" not in plano or not isinstance(plano["dias_de_treino"], list) or not plano["dias_de_treino"]:
        raise ValueError("Campo 'dias_de_treino' deve ser uma lista nao-vazia")
    if "sugestoes_nutricionais" not in plano:
        raise ValueError("Campo obrigatorio 'sugestoes_nutricionais' ausente")


def generate_training_plan(user, preferencias: Optional[dict] = None) -> Dict[str, Any]:
    prompt = _build_prompt(user, preferencias)

    gemini_quota.check_and_increment()
    logger.info(f"Chamando Gemini: user_id={user.id}")
    response_text = _call_gemini_api(prompt, response_schema=PlanoIAResponseSchema)

    try:
        plano = json.loads(response_text)
    except json.JSONDecodeError as e:
        logger.error(f"IA retornou JSON invalido: linha {e.lineno}, col {e.colno}: {e.msg} | preview={response_text[:200]!r}")
        raise ValueError(f"JSON invalido na linha {e.lineno}: {e.msg}")

    _validate_plano(plano)
    if not plano.get("explicacao_ia"):
        plano["explicacao_ia"] = "Plano personalizado gerado com base em seus dados de perfil."

    plano = _normalize_plano(plano)
    logger.info(f"Plano gerado: user_id={user.id}, {len(plano['dias_de_treino'])} dias")
    return plano
