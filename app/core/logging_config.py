"""
Простая настройка логов.
"""

import logging as py_logging


def configure_logging() -> None:
    """Включает базовую конфигурацию логирования."""
    py_logging.basicConfig(
        level=py_logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
