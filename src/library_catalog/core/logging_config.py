"""
Настройка логирования приложения.
"""

import logging
import sys


def setup_logging() -> None:
    """Настроить логирование приложения."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("app.log", encoding="utf-8"),
        ],
    )

    # Устанавливаем уровень для SQLAlchemy
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
