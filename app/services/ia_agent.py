# app/services/ia_agent.py

from google.genai import types
from google.genai.client import Client as GeminiClient
from app.core.config import settings
from string import Template
import re
from urllib.parse import quote_plus
import logging
import json
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

JSON_EXAMPLE = """{
    "nome_da_rotina": "Ex.: Programa de Hipertrofia",
    "dias_de_treino": [
        {
            "foco_muscular": "Ex.: Peito e Tríceps",
            "identificacao": "Ex.: Dia A",
            "exercicios": [
                {
                    "nome": "Ex.: Supino reto com barra",
                    "series": "Ex.: 4x",
                    "repeticoes": "Ex.: 8-12",
                    "descanso_segundos": 90,
                    "detalhes_execucao": "Ex.: Manter os ombros retraídos e controlar o movimento",
                    "video_url": "Ex.: https://www.youtube.com/results?search_query=como+fazer+supino+reto+barra"
                }
            ]
        }
    ],
    "sugestoes_nutricionais": {
        "pre_treino": {
                "opcao_economica": {
                "nome": "Ex.: Banana com aveia",
                "custo_estimado": "Ex.: R$ 3,00",
                "ingredientes": ["Ex.: 1 banana", "Ex.: 2 colheres de aveia", "Ex.: 1 copo de água"],
                "link_receita": "Ex.: https://www.google.com/search?q=como+fazer+banana+com+aveia",
                "explicacao": "Ex.: Combinação rápida de carboidratos para energia"
            },
            "opcao_equilibrada": {
                "nome": "Ex.: Pão integral com pasta de amendoim",
                "custo_estimado": "Ex.: R$ 5,00",
                "ingredientes": ["Ex.: 2 fatias de pão integral", "Ex.: 2 colheres de pasta de amendoim"],
                "link_receita": "Ex.: https://www.google.com/search?q=como+fazer+pao+integral+pasta+amendoim",
                "explicacao": "Ex.: Carboidratos e gorduras saudáveis"
            },
            "opcao_premium": {
                "nome": "Ex.: Tapioca com queijo e peito de peru",
                "custo_estimado": "Ex.: R$ 8,00",
                "ingredientes": ["Ex.: 3 colheres de goma de tapioca", "Ex.: 30g queijo branco", "Ex.: 50g peito de peru"],
                "link_receita": "Ex.: https://www.google.com/search?q=como+fazer+tapioca+queijo+peru",
                "explicacao": "Ex.: Proteínas e carboidratos de qualidade"
            }
        },
        "pos_treino": {
            "opcao_economica": {
                "nome": "Ex.: Arroz com ovo",
                "custo_estimado": "Ex.: R$ 4,00",
                "ingredientes": ["Ex.: 1 xícara de arroz", "2 ovos", "sal a gosto"],
                "link_receita": "Ex.: https://www.google.com/search?q=como+fazer+arroz+com+ovo",
                "explicacao": "Ex.: Proteína e carboidratos para recuperação"
            },
            "opcao_equilibrada": {
                "nome": "Ex.: Frango grelhado com batata doce",
                "custo_estimado": "Ex.: R$ 7,00",
                "ingredientes": ["Ex.: 150g frango", "200g batata doce", "temperos"],
                "link_receita": "Ex.: https://www.google.com/search?q=como+fazer+frango+batata+doce",
                "explicacao": "Ex.: Refeição completa para recuperação muscular"
            },
            "opcao_premium": {
                "nome": "Ex.: Salmão com quinoa e legumes",
                "custo_estimado": "Ex.: R$ 15,00",
                "ingredientes": ["Ex.: 150g salmão", "1 xícara quinoa", "legumes variados"],
                "link_receita": "Ex.: https://www.google.com/search?q=como+fazer+salmao+quinoa+legumes",
                "explicacao": "Ômega-3 e proteínas de alto valor biológico"
            }
        }
    }
}"""

_gemini_client = None


def get_gemini_client() -> GeminiClient:
    """
    Inicializa o cliente gemini com lazy loading.
    Garante que a API key está configurada corretamente.
    """
    global _gemini_client

    if _gemini_client is None:
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("API_KEY não configurada.")
        try:
            _gemini_client = GeminiClient(api_key=api_key)
            logger.info("Cliente gemini inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar gemini: {e}")
            raise

    return _gemini_client

# Tenta inicializar na importação para evitar cold start
try:
    if settings.GEMINI_API_KEY:
        get_gemini_client()
except Exception:
    pass # Falha silenciosa na importação, erro real aparecerá na chamada


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)
def _call_gemini_api(prompt: str) -> str:
    """
    Chama a API gemini com retry automático.
    """

    try:
        client = get_gemini_client()

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.5,
                max_output_tokens=8192,
                response_mime_type="application/json",
            ),
        )

        return response.text

    except Exception as e:
        logger.error(f"Erro ao chamar API gemini: {e}")
        if "429" in str(e):
            raise ValueError("Serviço de IA sobrecarregado. Tente novamente em alguns instantes.")
        if "500" in str(e) or "503" in str(e):
            raise ValueError("Serviço de IA indisponível no momento.")
        
        raise ValueError(f"Erro na comunicação com IA: {str(e)}")


def obter_preferencias_usuario(usuario_id: int, db: Session) -> dict:
    """
    Busca preferências do usuário baseadas em feedbacks anteriores.
    
    Args:
        usuario_id: ID do usuário
        db: Sessão do banco de dados
    
    Returns:
        Dict com listas de exercícios e refeições que o usuário gostou/não gostou
    """
    from app.database.models.feedback import Feedback
    
    try:
        feedbacks = db.query(Feedback).filter(
            Feedback.usuario_id == usuario_id
        ).all()
        
        preferencias = {
            "exercicios_evitar": [],
            "exercicios_preferidos": [],
            "refeicoes_evitar": [],
            "refeicoes_preferidas": []
        }
        
        for feedback in feedbacks:
            if feedback.tipo == "exercicio":
                if feedback.gostou:
                    preferencias["exercicios_preferidos"].append(feedback.item_nome)
                else:
                    preferencias["exercicios_evitar"].append(feedback.item_nome)
            elif feedback.tipo == "refeicao":
                if feedback.gostou:
                    preferencias["refeicoes_preferidas"].append(feedback.item_nome)
                else:
                    preferencias["refeicoes_evitar"].append(feedback.item_nome)
        
        logger.info(f"Preferências carregadas para usuário {usuario_id}: "
                   f"{len(preferencias['exercicios_evitar'])} ex. evitar, "
                   f"{len(preferencias['refeicoes_evitar'])} ref. evitar")
        
        return preferencias
        
    except Exception as e:
        logger.error(f"Erro ao buscar preferências: {e}")
        return {
            "exercicios_evitar": [],
            "exercicios_preferidos": [],
            "refeicoes_evitar": [],
            "refeicoes_preferidas": []
        }


def generate_training_plan(
    nome: str,
    altura: float,
    peso: float,
    idade: int,
    disponibilidade: int,
    local: str,
    objetivo: str,
    preferencias: Optional[dict] = None,
) -> Dict[str, Any]:

    altura_metros = altura / 100

    imc = peso / (altura_metros**2)

    local_map = {"academia": "Academia", "casa": "Em casa", "arLivre": "Ao ar livre"}

    objetivo_map = {
        "perder": "Perder peso",
        "ganhar": "Ganhar peso",
        "hipertrofia": "Hipertrofia muscular",
        "definicao": "Definição muscular",
    }

    local_descricao = local_map.get(local, local)
    objetivo_descricao = objetivo_map.get(objetivo, objetivo)

    prompt_template = Template(
        """
        Você é uma API de backend. Retorne APENAS um objeto JSON válido, sem texto antes ou depois.

        DADOS DO USUÁRIO:
        Nome: $NOME | Altura: $ALTURA cm | Peso: $PESO kg | Idade: $IDADE anos
        IMC: $IMC | Frequência: $FREQUENCIA x/semana | Local: $LOCAL | Objetivo: $OBJETIVO

        SUAS OBRIGAÇÕES:
        1. Retornar EXCLUSIVAMENTE um JSON válido, sem introduções, comentários ou explicações
        2. Gerar $FREQUENCIA dias de treino com 5-6 exercícios cada
        3. Cada exercício: nome, series (texto), repeticoes (texto), descanso_segundos (número), detalhes_execucao, video_url
        4. Incluir sugestões nutricionais com 3 opções cada (pre_treino e pos_treino)
        5. VERIFICAR TÓDAS AS VÍRGULAS E CHAVES - JSON DEVE SER 100% VÁLIDO

        REGRAS CRÍTICAS DE JSON:
        ✓ Use aspas duplas APENAS
        ✓ TODAS as chaves e valores string com aspas duplas
        ✓ Números SEM aspas: "descanso_segundos": 60 (não "60")
        ✓ VERIFIQUE cada vírgula - não pode haver vírgula antes de } ou ]
        ✓ CADA valor string deve estar entre aspas: "valor"
        ✓ Arrays com [],  Objects com {}
        ✓ Sem quebras de linha dentro de strings - usar espaços normais
        ✗ Não adicione NADA fora do JSON

        ESTRUTURA ESPERADA:
        $JSON_EXAMPLE

        nesse exemplo — gere variações e substitua valores por opções relevantes ao usuário. 
        
        IMPORTANTE SOBRE AS REFEIÇÕES:
        - SEJA CRIATIVO! Não repita sempre "Banana com aveia" ou "Frango com batata doce".
        - Varie as fontes de proteína (ovos, iogurte, atum, carne moída, whey, queijo cottage, tofu, lentilha).
        - Varie as fontes de carboidrato (pão, tapioca, cuscuz, macarrão, arroz, batata inglesa, mandioca, frutas variadas).
        - Considere opções práticas e saborosas.
        - Tente surpreender com combinações diferentes, mas acessíveis.
        $PREFERENCIAS

        COMECE COM { E TERMINE COM } - NADA MAIS!
    """
    )
    
    preferencias_text = ""
    if preferencias:
        if preferencias.get("exercicios_evitar"):
            exercicios_evitar = ", ".join(preferencias["exercicios_evitar"][:10])  # Limitar a 10
            preferencias_text += f"""

RESTRIÇÃO CRÍTICA - EXERCÍCIOS PROIBIDOS:
O usuário JÁ TESTOU e NÃO GOSTOU dos seguintes exercícios. JAMAIS os inclua:
{exercicios_evitar}

Substitua por exercícios alternativos que trabalhem os mesmos grupos musculares.
"""
        
        if preferencias.get("refeicoes_evitar"):
            refeicoes_evitar = ", ".join(preferencias["refeicoes_evitar"][:10])
            preferencias_text += f"""

RESTRIÇÃO CRÍTICA - REFEIÇÕES PROIBIDAS:
O usuário NÃO GOSTA das seguintes refeições/ingredientes. EVITE COMPLETAMENTE:
{refeicoes_evitar}

Sugira alternativas diferentes com outras proteínas e carboidratos.
"""
    
    prompt = prompt_template.substitute(
        NOME=nome,
        ALTURA=altura,
        PESO=peso,
        IDADE=idade,
        IMC=f"{imc:.2f}",
        FREQUENCIA=disponibilidade,
        LOCAL=local_descricao,
        OBJETIVO=objetivo_descricao,
        JSON_EXAMPLE=JSON_EXAMPLE,
        PREFERENCIAS=preferencias_text,
    )

    try:
        logger.info(f"Gerando plano de treino para {nome}")
        response_text = _call_gemini_api(prompt)

        logger.debug(
            f"Resposta bruta da IA (primeiros 500 chars): {response_text[:500]}"
        )

        try:
            plano_dict = json.loads(response_text)
        except json.JSONDecodeError as json_err:
            logger.error("IA retornou JSON inválido")
            logger.error(
                f"Posição do erro: linha {json_err.lineno}, coluna {json_err.colno}"
            )
            logger.error(f"Mensagem: {json_err.msg}")

            lines = response_text.split("\n")
            if json_err.lineno <= len(lines):
                error_line = lines[json_err.lineno - 1]
                logger.error(f"Linha com erro: {error_line}")
                logger.error(f"Posição: {' ' * (json_err.colno - 1)}^")

            raise ValueError(
                f"A IA retornou uma resposta com JSON inválido. "
                f"Erro na linha {json_err.lineno}, coluna {json_err.colno}: {json_err.msg}"
            )

        if not isinstance(plano_dict, dict):
            raise ValueError("Resposta da IA não é um objeto JSON válido")

        if "nome_da_rotina" not in plano_dict:
            raise ValueError("Campo obrigatório 'nome_da_rotina' ausente na resposta")

        if "dias_de_treino" not in plano_dict:
            raise ValueError("Campo obrigatório 'dias_de_treino' ausente na resposta")

        if not isinstance(plano_dict["dias_de_treino"], list):
            raise ValueError("Campo 'dias_de_treino' deve ser uma lista")

        if len(plano_dict["dias_de_treino"]) == 0:
            raise ValueError("Campo 'dias_de_treino' não pode estar vazio")

        if "sugestoes_nutricionais" not in plano_dict:
            raise ValueError(
                "Campo obrigatório 'sugestoes_nutricionais' ausente na resposta"
            )

        plano = plano_dict

        def ensure_search_url(url: str, query: str, target: str) -> str:
            if not url:
                if target == "youtube":
                    return f"https://www.youtube.com/results?search_query=como+fazer+{quote_plus(query)}"
                return f"https://www.google.com/search?q=como+fazer+{quote_plus(query)}"

            if target == "youtube" and re.search(
                r"youtube\.com/results\?search_query=", url
            ):
                return url
            if target == "google" and re.search(r"google\.com/search\?q=", url):
                return url

            if target == "youtube":
                return f"https://www.youtube.com/results?search_query=como+fazer+{quote_plus(query)}"
            return f"https://www.google.com/search?q=como+fazer+{quote_plus(query)}"

        if isinstance(plano, dict) and "dias_de_treino" in plano:
            for dia in plano.get("dias_de_treino", []):
                for ex in dia.get("exercicios", []):
                    nome_ex = ex.get("nome", "")
                    descanso = ex.get("descanso_segundos")
                    if isinstance(descanso, str) and descanso.isdigit():
                        ex["descanso_segundos"] = int(descanso)
                    elif not isinstance(descanso, int):
                        ex["descanso_segundos"] = 60

                    ex["video_url"] = ensure_search_url(
                        ex.get("video_url"), nome_ex, "youtube"
                    )

        if isinstance(plano, dict) and "sugestoes_nutricionais" in plano:
            for timing in ("pre_treino", "pos_treino"):
                block = plano["sugestoes_nutricionais"].get(timing, {})
                for key, meal in list(block.items()):
                    nome_ref = meal.get("nome") or key
                    meal["link_receita"] = ensure_search_url(
                        meal.get("link_receita"), nome_ref, "google"
                    )

        logger.info(f"Plano gerado e validado com sucesso para {nome}")
        logger.info(f"Plano contém {len(plano['dias_de_treino'])} dias de treino")
        return plano

    except ValueError:
        raise

    except Exception as e:
        logger.error(f"Erro inesperado ao gerar plano: {e}")
        raise ValueError(f"Erro ao processar resposta da IA: {str(e)}")
