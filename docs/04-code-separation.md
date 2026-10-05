# 04. Разделение кода и Labeler

> Источники:
> - <https://vkbottle.readthedocs.io/ru/latest/tutorial/code-separation/>
> - <https://vkbottle.readthedocs.io/ru/latest/high-level/bot/labeler/>

> **Примечание.** Разделение кода — очень важная вещь для создания структуры проекта.

Чтобы делать это, в vkbottle можно использовать составляющие фреймворка отдельно от `Bot`.

Разделение кода, кроме того может быть очень грамотно использовано для создания локальных изменений в лейблере, например `auto_rules` поможет установить правила, которые будут накладываться на все хендлеры сообщений.

> **Внимание.** Правила в `auto_rules` распространяются только на хендлеры сообщений, для сырых евентов вам нужен `raw_event_auto_rules` и кастомные правила, работающие с ними.

## Стандартная иерархия файлов

Для удобства разработки больших проектов, рекомендуется использовать подобную структуру файлов:

```
/src/
├── handlers
│   ├── __init__.py
│   ├── admin.py
│   ├── chat.py
│   └── ping.py
├── bot.py
└── config.py
```

### `config.py`

Файл с конфигом, в котором будут храниться все глобальные переменные, которые будут использоваться в разных частях проекта:

```python
from vkbottle import API, BuiltinStateDispenser
from vkbottle.bot import BotLabeler

api = API("token")
labeler = BotLabeler()
state_dispenser = BuiltinStateDispenser()
```

> **Примечание.** В данном примере стейт диспенсер не используется, но объявлен для наглядности. Если вы хотите использовать его, то просто импортируйте из `config.py` и используйте в своих хендлерах. Не забудьте указать `state_dispenser` в `Bot` в `bot.py`.

### `handlers/ping.py`

```python
from config import labeler


@labeler.message(text="ping")
async def ping_handler(message):
    await message.answer("pong")
```

### `handlers/chat.py`

1. Добавим в `auto_rules` правило, которое будет следить чтобы все сообщения шли только из чата
2. Создадим правило, которое будет получать информацию о чате и возвращать ее для всех хендлеров этого лейблера
3. Добавим несколько хендлеров

```python
from vkbottle.bot import BotLabeler, Message, rules
from vkbottle_types.objects import MessagesConversation


class ChatInfoRule(rules.ABCRule[Message]):
    async def check(self, message: Message) -> dict[str, Any]:
        chats_info = await message.ctx_api.messages.get_conversations_by_id(message.peer_id)
        return {"chat": chats_info.items[0]}


chat_labeler = BotLabeler()
chat_labeler.vbml_ignore_case = True
chat_labeler.auto_rules = [rules.PeerRule(from_chat=True), ChatInfoRule()]


@chat_labeler.message(command="самобан")
async def kick(message: Message, chat: MessagesConversation):
    await message.ctx_api.messages.remove_chat_user(message.chat_id, message.from_id)
    await message.answer(f"Участник самоустранился из {chat.chat_settings.title} по собственному желанию")


@chat_labeler.message(text="где я")
async def where_am_i(message: Message, chat: MessagesConversation):
    await message.answer(f"Вы в <<{chat.chat_settings.title}>>")
```

### `handlers/admin.py`

> Пусть эти команды будут доступны только, например, создателю бота.

```python
from vkbottle.bot import BotLabeler, Message, rules

admin_labeler = BotLabeler()
admin_labeler.auto_rules = [rules.FromPeerRule(1)]  # Допустим, вы являетесь Павлом Дуровым


@admin_labeler.message(command="halt")
async def halt(_):
    exit(0)
```

### `handlers/__init__.py`

```python
from .chat import chat_labeler
from .admin import admin_labeler
from .ping import labeler

# Если использовать глобальный лейблер, то все хендлеры будут зарегистрированы в том же порядке, в котором они были импортированы
__all__ = ("admin_labeler", "chat_labeler", "labeler")
```

### `bot.py`

```python
from vkbottle import Bot
from config import api, state_dispenser, labeler
from handlers import chat_labeler, admin_labeler
```

> Так как мы создали файл `__init__.py` в папке `handlers`, интерпретатор выполнит код в `echo.py` и нам не нужно будет импортировать лейблер оттуда.

Загружаем хендлеры в глобальный лейблер:

```python
labeler.load(chat_labeler)
labeler.load(admin_labeler)
```

Создаем инстанс бота и указываем, какой лейблер и стейт диспенсер использовать:

```python
bot = Bot(
    api=api,
    labeler=labeler,
    state_dispenser=state_dispenser,
)
```

Запускаем:

```python
bot.run_forever()
```

---

## Bot-Labeler

Удобная оболочка над роутерами. С помощью лейблера создаются хендлеры. Может быть использовано в качестве портабельного диспатчера.

Имеет метод `load`, который должен загружать хендлеры и мидлвари в текущий лейблер из переданного. Может быть использовано для разбивания кода на много частей.

### `bot.py`

```python
from vkbottle import Bot
from routes import labelers

bot = Bot("token")
for custom_labeler in labelers:
    bot.labeler.load(custom_labeler)

bot.run_forever()
```

### `routes/__init__.py`

```python
from . import greetings, goodbyes

labelers = [greetings.bl, goodbyes.bl]
```

### `routes/greetings.py`

```python
from vkbottle.bot import BotLabeler, Message

bl = BotLabeler()


@bl.message(text=["привет", "хай", "здравствуй"])
async def greeting(message: Message):
    await message.answer("Привет, друг")
```

### `routes/goodbyes.py`

```python
from vkbottle.bot import BotLabeler, Message

bl = BotLabeler()


@bl.message(text=["пока", "до свидания"])
async def greeting(message: Message):
    await message.answer("До новых встреч")
```

---

## Blueprint (устарел)

> Источник: <https://vkbottle.readthedocs.io/ru/latest/high-level/bot/blueprint/>

Блупринты являются **устаревшей частью фреймворка** и будут удалены в следующих версиях. Узнать о новом способе разделения кода можно в [туториале по разделению кода](https://vkbottle.readthedocs.io/ru/latest/tutorial/code-separation/).

---

## Экземплы по этой части туториала

- [code_separation](https://github.com/vkbottle/vkbottle/tree/master/examples/high-level/code_separation)

---

Далее: [05. Клавиатуры и вложения](./05-keyboards.md)
