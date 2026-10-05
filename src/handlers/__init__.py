"""Хендлеры бота.

Порядок важен: хендлеры подключаются через `labeler.load()` и добавляются
в общий список, поэтому сначала идут приветствия, затем AI-обработчики.
"""

from . import chat, greeting

labelers = [greeting.bl, chat.bl]

__all__ = ("chat", "greeting", "labelers")
