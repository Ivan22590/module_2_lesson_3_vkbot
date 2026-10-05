"""Ответы на входящие сообщения при помощи AI."""

from __future__ import annotations

from vkbottle.bot import BotLabeler, Message, rules

from .. import ai
from .greeting import take_greeting

bl = BotLabeler()

AI_ERROR_TEXT = (
    "Не смог получить ответ от нейросети. "
    "Попробуйте, пожалуйста, написать ещё раз чуть позже."
)

# Обрабатываем только текстовые сообщения: на стикеры и вложения ответить нечем
HAS_TEXT = rules.FuncRule(lambda message: bool(message.text))


class ReplyToBotRule(rules.ABCRule[Message]):
    """Срабатывает, когда пользователь ответил именно на сообщение бота.

    Отвечать на чужие цитаты в общей беседе было бы спамом, поэтому проверяем
    автора цитируемого сообщения: он должен совпадать с id сообщества.
    """

    async def check(self, event: Message) -> bool:
        reply = event.reply_message
        if reply is None or not event.group_id:
            return False
        return reply.from_id == -event.group_id


async def _ask_ai(message: Message) -> str:
    try:
        return await ai.ask(message.text, message.peer_id)
    except ai.AIError:
        return AI_ERROR_TEXT


@bl.private_message(HAS_TEXT)
async def private_message(message: Message) -> str:
    """Личные сообщения: первое — приветствие, все остальные — ответ модели."""
    if (greeting := take_greeting(message.peer_id)) is not None:
        return greeting
    return await _ask_ai(message)


@bl.chat_message(rules.MentionRule(mention_only=False), HAS_TEXT)
async def chat_mention(message: Message) -> str:
    """Беседа: бота упомянули в сообщении."""
    return await _ask_ai(message)


@bl.chat_message(ReplyToBotRule(), HAS_TEXT)
async def chat_reply(message: Message) -> str:
    """Беседа: пользователь ответил на сообщение бота."""
    return await _ask_ai(message)
