"""Приветствие новых пользователей — в беседах и в личных сообщениях."""

from __future__ import annotations

from loguru import logger
from vkbottle import VKAPIError
from vkbottle.bot import BotLabeler, Message

bl = BotLabeler()

# События ВК, с которыми приходит «новый участник беседы»
NEW_MEMBER_ACTIONS = [
    "chat_invite_user",
    "chat_invite_user_by_link",
    "chat_invite_user_by_message_request",
]

GREETING_PRIVATE = (
    "Привет!👋 Я AI-помощник.\n"
    "Напиши мне любое сообщение — отвечу с помощью нейросети."
)
GREETING_MEMBER = "Добро пожаловать, {name}! Рады видеть тебя здесь 👋"
GREETING_MEMBER_UNNAMED = "Кто-то присоединился к беседе — привет! 👋"
GREETING_BOT_ADDED = (
    "Привет! Я подключился к беседе.\n"
    "Позовите меня упоминанием или ответьте на моё сообщение — отвечу."
)
GREETING_GROUP_ADDED = "Новое сообщество в беседе — поздороваемся! 👋"

# peer_id, которых уже поздоровались. Память живёт, пока работает процесс:
# после перезапуска бот поприветствует собеседников заново.
_greeted: set[int] = set()


def take_greeting(peer_id: int) -> str | None:
    """Приветствие для первого сообщения собеседника, иначе None.

    Вызывается из AI-хендлера (handlers/chat.py), потому что хендлеры блокирующие:
    отдельный хендлер-приветствие перехватил бы первое сообщение и модель бы его
    не увидела. Приветствие отправляется вместо ответа модели ровно один раз.
    """
    if peer_id in _greeted:
        return None
    _greeted.add(peer_id)
    return GREETING_PRIVATE


async def _first_name(message: Message, user_id: int) -> str | None:
    # Важно: user_ids — четвёртый параметр метода (после fields, from_group_id,
    # name_case), поэтому позиционный вызов users.get(user_id) привяжется к fields
    # и вернёт пустой список.
    try:
        users = await message.ctx_api.users.get(user_ids=user_id)
    except VKAPIError as error:
        logger.warning("Не удалось получить имя пользователя {}: {}", user_id, error.error_msg)
        return None
    return users[0].first_name if users else None


@bl.chat_message(action=NEW_MEMBER_ACTIONS)
async def greet_chat_member(message: Message) -> str:
    """Приветствуем участника, которого только что добавили в беседу."""
    member_id = message.action.member_id if message.action else None

    if member_id is None:
        return GREETING_MEMBER_UNNAMED

    # Отрицательный id — сообщество (в том числе сам бот)
    if member_id < 0:
        if message.group_id and member_id == -message.group_id:
            return GREETING_BOT_ADDED
        return GREETING_GROUP_ADDED

    name = await _first_name(message, member_id)
    return GREETING_MEMBER.format(name=name) if name else GREETING_MEMBER_UNNAMED
