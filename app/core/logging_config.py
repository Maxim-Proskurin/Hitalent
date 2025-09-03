"""Минимальная конфигурация логирования."""

from __future__ import annotations

import logging


def configure_logging() -> None:
    """Включает структурированное логирование."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
