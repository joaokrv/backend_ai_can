"""Sanitizadores contra Prompt Injection — whitelist agressiva de caracteres permitidos"""

import re


# Padrão para nome de usuário: apenas letras (com acentos), espaços, hífen, apóstrofo
# Exemplos válidos: "João Silva", "Maria-José", "D'Ávila", "José Luis"
NOME_PATTERN = re.compile(r"^[A-Za-zÀ-ÿ \'-]{2,100}$")

# Padrão para item_nome (exercício ou refeição): letras, números, espaços, hífen, apóstrofo
# Exemplos válidos: "Supino Reto", "Rosca Direta 20kg", "Frango Grelhado", "Pão Integral"
ITEM_NOME_PATTERN = re.compile(r"^[A-Za-zÀ-ÿa-z0-9\s'\-\(\)\.,/#]{2,255}$")

# Padrão para lesões/cuidados: texto mais permissivo que nome,
# mas agressivo contra prompt injection (máx 500 chars, sem newlines/tabs)
LESOES_PATTERN = re.compile(r"^[A-Za-zÀ-ÿ0-9\s\.,;:\-\(\)\!\?\']{0,500}$")


def _sanitize_prompt_injection(text: str | None) -> str | None:
    """
    Detecta e neutraliza tentativas comuns de jailbreak/prompt injection.
    Suporta termos em Inglês, Português, Espanhol e Francês.
    Substitui padrões maliciosos por uma tag segura.
    """
    if not text:
        return text
    # Pattern heurístico multilíngue: ações imperativas seguidas de alvos do sistema
    pattern = (
        r"(?i)("
        r"ignore|forget|disregard|override|bypass|"  # EN
        r"esquece|esqueça|desconsidere|sobrescreva|substitua|burle|desative|"  # PT
        r"olvida|ignora|anula|evita|desactiva|saltar|burlar|"  # ES
        r"oublie|annule|contourne|desactive|désactive"  # FR
        r").{0,30}("
        r"instruction|prompt|context|above|rule|system|"  # EN
        r"instrução|instruçao|instrucoes|instruções|comando|contexto|anterior|anteriores|acima|regra|regras|sistema|"  # PT
        r"instruccion|instrucciones|regla|reglas|sistema|arriba|"  # ES
        r"règle|règles|regle|regles|contexte|système|systeme|commande|commandes|précédent|precedent|precedente|ci-dessus"  # FR
        r")"
    )
    return re.sub(pattern, "[FILTRADO_POR_SEGURANCA]", text)


def safe_nome(value: str, field_name: str = "nome") -> str:
    """
    Sanitiza campo de nome com whitelist agressiva.
    Rejeita qualquer caractere que não seja letra, espaço, hífen ou apóstrofo.

    Args:
        value: string a validar
        field_name: nome do campo (para mensagem de erro)

    Returns:
        string sanitizada e validada

    Raises:
        ValueError: se contiver caracteres inválidos ou tamanho fora dos limites
    """
    value = value.strip()

    if not value:
        raise ValueError(f"{field_name} não pode estar vazio")

    if not NOME_PATTERN.match(value):
        raise ValueError(
            f"{field_name} contém caracteres inválidos. "
            "Use apenas letras (com acentos), espaços, hífen e apóstrofo. "
            "Exemplos válidos: 'João Silva', 'Maria-José', 'D'Ávila'"
        )

    return value


def safe_item_nome(value: str) -> str:
    """
    Sanitiza nome de item (exercício ou refeição) com whitelist agressiva.
    Rejeita qualquer caractere que não seja letra, número, espaço, hífen ou apóstrofo.

    Args:
        value: string a validar

    Returns:
        string sanitizada e validada

    Raises:
        ValueError: se contiver caracteres inválidos ou tamanho fora dos limites
    """
    value = value.strip()

    if not value:
        raise ValueError("Nome do item não pode estar vazio")

    if not ITEM_NOME_PATTERN.match(value):
        raise ValueError(
            "Nome do item contém caracteres inválidos. "
            "Use apenas letras, números, espaços, hífen e apóstrofo. "
            "Exemplos: 'Supino Reto', 'Frango Grelhado', 'Pão Integral 20g'"
        )

    return value


def safe_comentario(value: str, max_length: int = 500) -> str:
    """
    Sanitiza comentário/feedback com remoção de caracteres perigosos.
    Mais permissivo que safe_nome, mas remove quebras de linha e padrões de jailbreak.

    Args:
        value: string a validar
        max_length: tamanho máximo permitido

    Returns:
        string sanitizada

    Raises:
        ValueError: se exceder tamanho máximo
    """
    if not value:
        return ""  # comentário opcional

    # Remove quebras de linha e controles (só preserva espaços normais)
    value = re.sub(r"[\r\n\t]+", " ", value)

    # Remove múltiplos espaços consecutivos
    value = re.sub(r" +", " ", value).strip()

    if len(value) > max_length:
        raise ValueError(f"Comentário não pode exceder {max_length} caracteres")

    # Neutraliza tentativas de prompt injection
    value = _sanitize_prompt_injection(value)

    return value


def safe_lesoes(value: str | None) -> str | None:
    """
    Sanitiza descrição de lesões/cuidados com whitelist de caracteres permitidos.
    Mais permissivo que safe_nome (permite pontuação), mas agressivo contra prompt injection.

    Args:
        value: string a validar ou None

    Returns:
        string sanitizada ou None

    Raises:
        ValueError: se contiver caracteres inválidos ou exceder 500 caracteres
    """
    if not value:
        return None

    # Remove quebras de linha, tabs e controles
    value = re.sub(r"[\r\n\t]+", " ", value).strip()

    # Remove múltiplos espaços consecutivos
    value = re.sub(r" +", " ", value)

    if not LESOES_PATTERN.match(value):
        raise ValueError(
            "Descrição de lesões/cuidados contém caracteres inválidos. "
            "Use apenas letras, números, espaços e pontuação básica (,.;:-()!?')"
        )

    # Neutraliza tentativas de prompt injection
    value = _sanitize_prompt_injection(value)

    return value
