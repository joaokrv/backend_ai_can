# app/services/ia_agent.py
# A lógica que cruza dados e gera sugestões

from cerebras.cloud.sdk import Cerebras
from app.core.config import settings
import logging
import json
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

# Cliente Cerebras (inicializado sob demanda)
_cerebras_client = None


def get_cerebras_client() -> Cerebras:
    """
    Inicializa o cliente Cerebras com lazy loading.
    Garante que a API key está configurada corretamente.
    
    Returns:
        Cerebras: Cliente inicializado
    
    Raises:
        ValueError: Se CEREBRAS_API_KEY não estiver configurada
    """
    global _cerebras_client
    
    if _cerebras_client is None:
        api_key = settings.CEREBRAS_API_KEY
        if not api_key:
            raise ValueError(
                "CEREBRAS_API_KEY não configurada. "
                "Configure em .env ou variáveis de ambiente."
            )
        try:
            _cerebras_client = Cerebras(api_key=api_key)
            logger.info("Cliente Cerebras inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar Cerebras: {e}")
            raise
    
    return _cerebras_client


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
def _call_cerebras_api(prompt: str) -> str:
    """
    Chama a API Cerebras com retry automático.
    
    Args:
        prompt: Prompt para enviar à IA
    
    Returns:
        str: Resposta da API em formato texto
    
    Raises:
        ValueError: Se houver erro na comunicação com a API
    """
    try:
        client = get_cerebras_client()
        
        response = client.chat.completions.create(
            model="llama3.1-70b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=4096
        )
        
        logger.info("Resposta recebida da API Cerebras com sucesso")
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Erro ao chamar API Cerebras: {e}")
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
    """
    Função principal do agente de IA que processa os dados
    do usuário e retorna um plano de treino personalizado
    com sugestões de refeições pré e pós-treino.
    
    Args:
        nome: Nome do usuário
        altura: Altura em centímetros (ex: 175)
        peso: Peso em kg
        idade: Idade em anos
        disponibilidade: Quantas vezes por semana (1-7)
        local: Local de treino ("academia", "casa", "arLivre")
        objetivo: Objetivo ("perder", "ganhar", "hipertrofia")
    
    Returns:
        Dict: Plano de treino estruturado com exercícios e refeições
    
    Raises:
        ValueError: Se os dados forem inválidos ou API falhar
    """
    
    # Converter altura de cm para metros
    altura_metros = altura / 100
    
    # Calcular IMC (peso / altura²)
    imc = peso / (altura_metros ** 2)
    
    # Mapear valores do frontend para descrições legíveis
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
    
    # Construir prompt estruturado
    prompt = f"""
Você é um personal trainer e nutricionista especializado. Crie um plano de treino COMPLETO e DETALHADO em formato JSON para:

**Perfil do Aluno:**
- Nome: {nome}
- Altura: {altura}cm ({altura_metros:.2f}m)
- Peso: {peso}kg
- Idade: {idade} anos
- IMC: {imc:.2f}
- Frequência: {disponibilidade}x por semana
- Local: {local_descricao}
- Objetivo: {objetivo_descricao}

**Instruções:**
1. Crie uma divisão de treino apropriada para {disponibilidade}x por semana
2. Para cada dia de treino, inclua 5-6 exercícios específicos
3. Cada exercício deve ter: nome, séries, repetições, descanso em segundos, detalhes de execução, e link do YouTube
4. Inclua sugestões nutricionais pré e pós-treino com 3 opções cada (econômica, equilibrada, premium)
5. Cada refeição deve ter: nome, custo estimado, ingredientes (array), link de receita, e explicação nutricional

**IMPORTANTE:** Retorne APENAS o JSON, sem texto adicional antes ou depois.

**Formato JSON esperado:**
{{
  "nome_da_rotina": "Nome da divisão (ex: Divisão ABC)",
  "dias_de_treino": [
    {{
      "identificacao": "Treino A - Segunda",
      "foco_muscular": "Grupos musculares trabalhados",
      "exercicios": [
        {{
          "nome": "Nome do exercício",
          "series": "3-4",
          "repeticoes": "10-12",
          "descanso_segundos": 60,
          "detalhes_execucao": "Como executar corretamente",
          "video_url": "https://www.youtube.com/results?search_query=nome+do+exercicio"
        }}
      ]
    }}
  ],
  "sugestoes_nutricionais": {{
    "pre_treino": {{
      "opcao_economica": {{
        "nome": "Nome da refeição",
        "custo_estimado": "Baixo/Médio/Alto",
        "ingredientes": ["ingrediente1", "ingrediente2"],
        "link_receita": "https://www.google.com/search?q=receita",
        "explicacao": "Por que essa refeição é adequada"
      }},
      "opcao_equilibrada": {{ ... }},
      "opcao_premium": {{ ... }}
    }},
    "pos_treino": {{
      "opcao_economica": {{ ... }},
      "opcao_equilibrada": {{ ... }},
      "opcao_premium": {{ ... }}
    }}
  }}
}}
"""
    
    try:
        # Chamar API
        logger.info(f"Gerando plano de treino para {nome}")
        response_text = _call_cerebras_api(prompt)
        
        # Extrair JSON da resposta
        # Remove markdown code blocks se existirem
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        # Parse JSON
        plano = json.loads(response_text)
        
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
