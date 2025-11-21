# app/services/ia_agent.py

from google.genai import types
from google.genai.client import Client as GeminiClient
from app.core.config import settings
from string import Template
import re
from urllib.parse import quote_plus
import logging
import json
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential

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
                temperature=0.3,
                max_output_tokens=8192,
                response_mime_type="application/json",
            ),
        )

        return response.text

    except Exception as e:
        logger.error(f"Erro ao chamar API gemini: {e}")
        raise ValueError(f"Erro ao processar requisição com IA: {str(e)}")


def generate_training_plan(
    nome: str,
    altura: float,
    peso: float,
    idade: int,
    disponibilidade: int,
    local: str,
    objetivo: str,
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

        OBSERVAÇÃO: Os valores dentro do JSON_EXAMPLE são APENAS exemplos de formato e valores;
        não limite as opções de receitas, nomes, ou campos similares apenas ao que aparece
        nesse exemplo — gere variações e substitua valores por opções relevantes ao usuário. Você deve sugerir sugestões diferentes e variadas.

        COMECE COM { E TERMINE COM } - NADA MAIS!
    """
    )

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
