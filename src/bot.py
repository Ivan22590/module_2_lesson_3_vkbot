"""Точка входа: создаём бота, подключаем лейблеры и запускаем LongPoll."""

from __future__ import annotations

import sys
from pathlib import Path

# Прямой запуск (python src/bot.py) делает файл модулем __main__, а не пакета src,
# поэтому относительные импорты здесь не работают. Добавляем корень проекта
# в sys.path и используем абсолютные импорты — так одинаково работают оба варианта:
#   python src/bot.py
#   python -m src.bot
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from loguru import logger
from vkbottle import Bot, BotPolling

from src import config
from src.handlers import labelers


def build_bot() -> Bot:
    polling = BotPolling(
        wait=config.LONGPOLL_WAIT,
        rps_delay=config.LONGPOLL_RPS_DELAY,
    )
    bot = Bot(token=config.VK_TOKEN, polling=polling)

    # По умолчанию у MessageView replace_mention = False: упоминание не вырезается
    # из текста и is_mentioned всегда False, то есть MentionRule не срабатывает.
    # Включаем — иначе бот в беседе не отреагирует на @упоминание.
    bot.labeler.message_view.replace_mention = True

    # Порядок load() определяет порядок проверки хендлеров
    for labeler in labelers:
        bot.labeler.load(labeler)

    return bot


def main() -> None:
    # loguru используется и самим vkbottle, так что настройка действует на всё
    logger.remove()
    logger.add(sys.stderr, level=config.LOG_LEVEL)

    bot = build_bot()
    logger.info(
        "Бот запускается (LongPoll, wait={} c), AI-модель: {}",
        config.LONGPOLL_WAIT,
        config.AI_MODEL,
    )
    bot.run()


if __name__ == "__main__":
    main()
