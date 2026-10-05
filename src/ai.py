"""Ответы AI: клиент ProxyAPI (OpenAI-совместимый) и память диалогов."""

from __future__ import annotations

from collections import deque

from loguru import logger
from openai import AsyncOpenAI

from . import config


class AIError(Exception):
    """Не удалось получить ответ от модели."""


# Один клиент на весь процесс: openai поддерживает переиспользование сессии
_client = AsyncOpenAI(
    api_key=config.PROXYAPI_API_KEY,
    base_url=config.PROXYAPI_BASE_URL,
)

# История диалогов по peer_id. deque с maxlen сам отбрасывает самые старые реплики,
# поэтому наружу не утекают сообщения, выпавшие из окна истории.
_history: dict[int, deque[dict[str, str]]] = {}


def dialog(peer_id: int) -> deque[dict[str, str]]:
    if peer_id not in _history:
        _history[peer_id] = deque(maxlen=config.AI_HISTORY_LIMIT)
    return _history[peer_id]


def forget(peer_id: int) -> None:
    """Забыть диалог с собеседником."""
    _history.pop(peer_id, None)


async def ask(text: str, peer_id: int) -> str:
    """Отправить реплику пользователя в ProxyAPI и вернуть ответ модели.

    История обновляется только после успешного ответа, чтобы сбой запроса
    не «съедал» реплику пользователя: повторная отправка сообщения заработает.
    """
    dialog_history = dialog(peer_id)
    messages: list[dict[str, str]] = [
        {"role": "system", "content": config.AI_SYSTEM_PROMPT},
        *dialog_history,
        {"role": "user", "content": text},
    ]

    try:
        response = await _client.chat.completions.create(
            model=config.AI_MODEL,
            messages=messages,
        )
    except Exception as error:
        logger.error("Запрос к ProxyAPI не удался (peer_id={}): {}", peer_id, error)
        raise AIError(str(error)) from error

    if not response.choices:
        logger.error("ProxyAPI не вернул вариантов ответа (модель {})", config.AI_MODEL)
        raise AIError("нет вариантов ответа")

    answer = (response.choices[0].message.content or "").strip()
    if not answer:
        logger.error("ProxyAPI вернул пустой ответ (модель {})", config.AI_MODEL)
        raise AIError("пустой ответ модели")

    dialog_history.append({"role": "user", "content": text})
    dialog_history.append({"role": "assistant", "content": answer})
    return answer
