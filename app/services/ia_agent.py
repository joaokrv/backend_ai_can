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
    "nome_da_rotina": "Programa de Hipertrofia",
    "dias_de_treino": [
        {
            "foco_muscular": "Peito e Tríceps",
            "identificacao": "Dia A",
            "exercicios": [
                {
                    "nome": "Supino reto com barra",
                    "series": "4x",
                    "repeticoes": "8-12",
                    "descanso_segundos": 90,
                    "detalhes_execucao": "Manter os ombros retraídos e controlar o movimento",
                    "video_url": "https://www.youtube.com/results?search_query=supino+reto+barra"
                }
            ]
        }
    ],
    "sugestoes_nutricionais": {
        "pre_treino": {
            "opcao_economica": {
                "nome": "Banana com aveia",
                "custo_estimado": "R$ 3,00",
                "ingredientes": ["1 banana", "2 colheres de aveia", "1 copo de água"],
                "link_receita": "https://www.google.com/search?q=banana+com+aveia",
                "explicacao": "Combinação rápida de carboidratos para energia"
            },
            "opcao_equilibrada": {
                "nome": "Pão integral com pasta de amendoim",
                "custo_estimado": "R$ 5,00",
                "ingredientes": ["2 fatias de pão integral", "2 colheres de pasta de amendoim"],
                "link_receita": "https://www.google.com/search?q=pao+integral+pasta+amendoim",
                "explicacao": "Carboidratos e gorduras saudáveis"
            },
            "opcao_premium": {
                "nome": "Tapioca com queijo e peito de peru",
                "custo_estimado": "R$ 8,00",
                "ingredientes": ["3 colheres de goma de tapioca", "30g queijo branco", "50g peito de peru"],
                "link_receita": "https://www.google.com/search?q=tapioca+queijo+peru",
                "explicacao": "Proteínas e carboidratos de qualidade"
            }
        },
        "pos_treino": {
            "opcao_economica": {
                "nome": "Arroz com ovo",
                "custo_estimado": "R$ 4,00",
                "ingredientes": ["1 xícara de arroz", "2 ovos", "sal a gosto"],
                "link_receita": "https://www.google.com/search?q=arroz+com+ovo",
                "explicacao": "Proteína e carboidratos para recuperação"
            },
            "opcao_equilibrada": {
                "nome": "Frango grelhado com batata doce",
                "custo_estimado": "R$ 7,00",
                "ingredientes": ["150g frango", "200g batata doce", "temperos"],
                "link_receita": "https://www.google.com/search?q=frango+batata+doce",
                "explicacao": "Refeição completa para recuperação muscular"
            },
            "opcao_premium": {
                "nome": "Salmão com quinoa e legumes",
                "custo_estimado": "R$ 15,00",
                "ingredientes": ["150g salmão", "1 xícara quinoa", "legumes variados"],
                "link_receita": "https://www.google.com/search?q=salmao+quinoa+legumes",
                "explicacao": "Ômega-3 e proteínas de alto valor biológico"
            }
        }
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
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.15,
                max_output_tokens=8192,
                response_mime_type="application/json"
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

        COMECE COM { E TERMINE COM } - NADA MAIS!
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
        
        # Remove markdown
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        elif response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        # Extrai JSON do texto
        def extract_json_from_text(text: str) -> str:
            start = text.find("{")
            end = text.rfind("}")
            if start == -1 or end == -1 or end <= start:
                return text
            return text[start : end + 1]

        raw_json_text = extract_json_from_text(response_text)
        
        raw_json_text = re.sub(r',\s*}', '}', raw_json_text)
        raw_json_text = re.sub(r',\s*]', ']', raw_json_text)

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
        logger.error(f"Posição do erro: caractere {e.pos}, coluna {e.colno}")
        start = max(0, e.pos - 100)
        end = min(len(raw_json_text), e.pos + 100)
        logger.error(f"Contexto do erro: ...{raw_json_text[start:end]}...")
        logger.error(f"JSON completo (primeiros 2000 chars): {raw_json_text[:2000]}")
        raise ValueError(
            "A IA retornou uma resposta inválida. Tente novamente."
        )
    
    except Exception as e:
        logger.error(f"Erro ao gerar plano: {e}")
        raise
