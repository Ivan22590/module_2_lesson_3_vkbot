"""Конфигурация бота: ключи и настройки читаются из .env в корне проекта."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import NoReturn

from dotenv import load_dotenv

# Ищем .env в корне проекта, чтобы запуск работал из любой рабочей директории
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def _fail(message: str) -> NoReturn:
    print(f"[config] {message}", file=sys.stderr)
    raise SystemExit(1)


def _require(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        _fail(f"не задана переменная {name}. Заполните .env (образец — в .env.example)")
    return value


def _int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        _fail(f"переменная {name} должна быть целым числом, получено: {raw!r}")


# --- ВКонтакте -----------------------------------------------------------------
# Токен сообщества: Управление -> Работа с API -> Ключи доступа
VK_TOKEN = _require("VK_TOKEN")

# --- ProxyAPI (https://proxyapi.ru/docs/openai-text-generation) ----------------
PROXYAPI_API_KEY = _require("PROXYAPI_API_KEY")
PROXYAPI_BASE_URL = os.getenv("PROXYAPI_BASE_URL", "https://api.proxyapi.ru/v1").rstrip("/")

# gpt-4.1-mini: у ProxyAPI идентификатор модели = "<вендор>/<модель>",
# поэтому модель записана как "openai/gpt-4.1-mini"
AI_MODEL = os.getenv("AI_MODEL", "openai/gpt-4.1-mini").strip()

AI_SYSTEM_PROMPT = os.getenv(
    "AI_SYSTEM_PROMPT",
    "Ты — дружелюбный AI-помощник внутри ВКонтакте. "
    "Отвечай кратко и по делу, на языке собеседника.",
).strip()

# Сколько последних реплик истории держать в памяти одного диалога
AI_HISTORY_LIMIT = _int("AI_HISTORY_LIMIT", 10)

# --- LongPoll ------------------------------------------------------------------
# Секунды ожидания ответа LongPoll (ВК ответит принудительно, даже если событий нет)
LONGPOLL_WAIT = _int("LONGPOLL_WAIT", 25)
# Задержка между запросами LongPoll в секундах (0 — без задержки)
LONGPOLL_RPS_DELAY = _int("LONGPOLL_RPS_DELAY", 0)

# --- Логирование ----------------------------------------------------------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").strip().upper() or "INFO"
