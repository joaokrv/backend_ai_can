"""Política de validação de senhas — força mínima + wordlist de senhas comuns"""

import re
from pathlib import Path


# Carregar wordlist de senhas comuns no startup
_WORDLIST_PATH = Path(__file__).parent / "wordlists" / "common_passwords.txt"
_COMMON_PASSWORDS_SET: set[str] = set()


def _load_common_passwords() -> None:
    """Carrega wordlist de senhas comuns em memória (executado uma única vez)"""
    global _COMMON_PASSWORDS_SET
    try:
        if _WORDLIST_PATH.exists():
            with open(_WORDLIST_PATH, "r", encoding="utf-8") as f:
                _COMMON_PASSWORDS_SET = {line.strip().lower() for line in f if line.strip()}
    except Exception as e:
        # Falha silenciosa na leitura, mas log de aviso
        import logging
        logging.warning(f"Não foi possível carregar wordlist de senhas comuns: {e}")
        # Garante que _COMMON_PASSWORDS_SET não fica vazio — pelo menos as mais comuns
        _COMMON_PASSWORDS_SET = {"password", "123456", "admin", "letmein", "welcome"}


# Carregar wordlist na importação
_load_common_passwords()


def validate_password(password: str) -> str:
    """
    Valida força da senha com requisitos:
    - Mínimo 10 caracteres
    - Pelo menos 1 letra maiúscula
    - Pelo menos 1 letra minúscula
    - Pelo menos 1 número
    - Pelo menos 1 caractere especial (!@#$%^&*)
    - NÃO está na lista de senhas comuns

    Raises:
        ValueError: com mensagem clara sobre qual requisito falhou
    """
    if len(password) < 10:
        raise ValueError("Senha deve ter no mínimo 10 caracteres")

    if not re.search(r"[A-Z]", password):
        raise ValueError("Senha deve conter pelo menos uma letra maiúscula (A-Z)")

    if not re.search(r"[a-z]", password):
        raise ValueError("Senha deve conter pelo menos uma letra minúscula (a-z)")

    if not re.search(r"\d", password):
        raise ValueError("Senha deve conter pelo menos um número (0-9)")

    if not re.search(r"[!@#$%^&*(),.?\"':{}|<>\-_+=\[\]\\;`~]", password):
        raise ValueError("Senha deve conter pelo menos um caractere especial (!@#$%^&* etc.)")

    if password.lower() in _COMMON_PASSWORDS_SET:
        raise ValueError("Senha é muito comum. Escolha uma combinação mais única")

    return password
