"""
Contador diário de chamadas à API Gemini.
Proteção contra cobranças acidentais — bloqueia antes de atingir o limite do free tier.
Reset automático à meia-noite UTC.
"""

import logging
from datetime import datetime, timezone
from threading import Lock

logger = logging.getLogger(__name__)


class GeminiDailyQuota:
    """
    Contador thread-safe de chamadas diárias à API Gemini.
    Funciona em memória (suficiente para instância única no Render free tier).
    """

    def __init__(self, daily_limit: int = 200):
        """
        Args:
            daily_limit: Máximo de chamadas por dia. Default 200 (margem de segurança
                         antes das 250 RPD do gemini-2.5-flash free tier).
        """
        self._limit = daily_limit
        self._count = 0
        self._date = self._today()
        self._lock = Lock()

    def _today(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _reset_if_new_day(self) -> None:
        today = self._today()
        if today != self._date:
            logger.info(f"Gemini quota: reset diário ({self._count} chamadas ontem)")
            self._count = 0
            self._date = today

    def check_and_increment(self) -> None:
        """
        Verifica se ainda há quota disponível e incrementa o contador.

        Raises:
            ValueError: Se o limite diário foi atingido.
        """
        with self._lock:
            self._reset_if_new_day()

            if self._count >= self._limit:
                logger.warning(
                    f"Gemini quota diária esgotada: {self._count}/{self._limit} chamadas hoje"
                )
                raise ValueError(
                    f"Limite diário de geração de planos atingido ({self._limit} planos/dia). "
                    "O serviço estará disponível novamente à meia-noite (UTC)."
                )

            self._count += 1
            remaining = self._limit - self._count
            logger.info(f"Gemini quota: {self._count}/{self._limit} chamadas hoje ({remaining} restantes)")

    @property
    def status(self) -> dict:
        """Retorna status atual da quota para monitoramento."""
        with self._lock:
            self._reset_if_new_day()
            return {
                "date": self._date,
                "used": self._count,
                "limit": self._limit,
                "remaining": max(0, self._limit - self._count),
                "exhausted": self._count >= self._limit,
            }


# Singleton — uma instância compartilhada por toda a aplicação
from app.core.config import settings

_daily_limit = getattr(settings, "GEMINI_DAILY_LIMIT", 200)
gemini_quota = GeminiDailyQuota(daily_limit=_daily_limit)
