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
JSON_EXAMPLE = '''{
        "nome_da_rotina": "Texto",
        "dias_de_treino": [
            {
                "foco_muscular": "Texto",
                "identificacao": "Texto",
                "exercicios": [
                    {
                        "nome": "Texto",
                        "series": "Texto",
                        "repeticoes": "Texto",
                        "descanso_segundos": 0,
                        "detalhes_execucao": "Texto puro",
                        "video_url": "https://www.youtube.com/results?search_query=nome+do+exercicio"
                    }
                ]
            }
        ],
        "sugestoes_nutricionais": {
            "pre_treino": {
                "opcao_economica": {
                    "nome": "Texto",
                    "custo_estimado": "Texto",
                    "ingredientes": ["item1", "item2"],
                    "link_receita": "https://www.google.com/search?q=nome+da+receita",
                    "explicacao": "Texto puro"
                }
            },
            "pos_treino": {}
        }
    }'''

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
            raise ValueError(
                "API_KEY não configurada."
            )
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
    reraise=True
)

def _call_gemini_api(prompt: str) -> str:
    """
    Chama a API gemini com retry automático.
    """

    try:
        client = get_gemini_client()
        
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.15,
                max_output_tokens=2048
            )
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
    objetivo: str
) -> Dict[str, Any]:
    
    altura_metros = altura / 100
    
    imc = peso / (altura_metros ** 2)
    
    local_map = {
        "academia": "Academia",
        "casa": "Em casa",
        "arLivre": "Ao ar livre"
    }
    
    objetivo_map = {
        "perder": "Perder peso",
        "ganhar": "Ganhar peso",
        "hipertrofia": "Hipertrofia muscular"
    }
    
    local_descricao = local_map.get(local, local)
    objetivo_descricao = objetivo_map.get(objetivo, objetivo)

    prompt_template = Template("""
        Você é uma API de backend: receba os dados do usuário e retorne apenas um objeto JSON (sem texto adicional).

        --- DADOS DO USUÁRIO ---
        Nome: $NOME
        Altura: $ALTURA cm
        Peso: $PESO kg
        Idade: $IDADE anos
        IMC: $IMC
        Frequência: $FREQUENCIA x/semana
        Local: $LOCAL
        Objetivo: $OBJETIVO

        --- REGRAS DE CONTEÚDO ---
        1) Gere uma divisão de treino apropriada para $FREQUENCIA x/semana;
        2) Cada dia deve conter 5-6 exercícios com: nome, séries, repetições, descanso_segundos (int), detalhes_execucao (texto), e video_url;
        3) video_url deve ser uma URL de PESQUISA do YouTube (ex: https://www.youtube.com/results?search_query=nome+do+exercicio);
        4) Inclua sugestões nutricionais (pre/pos) com 3 opções: economica, equilibrada, premium; cada refeição precisa de nome, custo_estimado, ingredientes (lista), link_receita (URL de pesquisa Google) e explicacao;

        --- REGRAS DE FORMATAÇÃO E SEGURANÇA (OBRIGATÓRIO) ---
        - A resposta deve ser EXCLUSIVAMENTE o JSON bruto, sem Markdown nem texto;
        - NÃO escreva introduções, notas ou conclusões; comece com "{" e termine com "}";
        - Strings apenas com texto puro (sem HTML ou formatação);
        - Se algum campo estiver ausente ou inválido, retorne um valor padrão (ex.: descanso_segundos = 60) em vez de texto explicativo.

        --- FORMATO JSON (ordem importante) ---
        $JSON_EXAMPLE
    """)

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
        
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        

        def extract_json_from_text(text: str) -> str:
            start = text.find("{")
            end = text.rfind("}")
            if start == -1 or end == -1 or end <= start:
                return text
            return text[start : end + 1]

        raw_json_text = extract_json_from_text(response_text)

        plano = json.loads(raw_json_text)

        def ensure_search_url(url: str, query: str, target: str) -> str:
            if not url:
                if target == "youtube":
                    return f"https://www.youtube.com/results?search_query={quote_plus(query)}"
                return f"https://www.google.com/search?q={quote_plus(query)}"

            if target == "youtube" and re.search(r"youtube\.com/results\?search_query=", url):
                return url
            if target == "google" and re.search(r"google\.com/search\?q=", url):
                return url

            if target == "youtube":
                return f"https://www.youtube.com/results?search_query={quote_plus(query)}"
            return f"https://www.google.com/search?q={quote_plus(query)}"

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
        
        logger.info(f"Plano gerado com sucesso para {nome}")
        return plano
        
    except json.JSONDecodeError as e:
        logger.error(f"Resposta da IA não é JSON válido: {e}")
        logger.debug(f"Resposta recebida: {response_text[:500]}...")
        raise ValueError(
            "A IA retornou uma resposta inválida. Tente novamente."
        )
    
    except Exception as e:
        logger.error(f"Erro ao gerar plano: {e}")
        raise
