# 10. Callback API

> Источники:
> - <https://vkbottle.readthedocs.io/ru/latest/tutorial/callback-bot/>
> - <https://vkbottle.readthedocs.io/ru/latest/low-level/callback/>
> - <https://vkbottle.readthedocs.io/ru/latest/tools/message-event/>

> **Внимание.** [Обязательно к прочтению](https://dev.vk.ru/api/callback/getting-started)
>
> У вас должен иметься собственный сервер с доменным именем. **DDNS работать не будет.** Также подразумевается наличие опыта в настройке веб-серверов.

## Подключение CallbackAPI к сообществу

1. Инициализировать параметры для настройки:

```python
import os

TOKEN = os.getenv("VK_TOKEN")  # ключ сообщества
url = os.getenv("VK_URL")  # url = "http://example.com/whateveryouwnant"
title = os.getenv("VK_TITLE")  # title = "server"
secret_key = os.getenv("VK_SECRET_KEY")  # опционально
```

2. Импортировать `BotCallback` из `vkbottle.callback` и указать параметры для настройки:

```python
from vkbottle.callback import BotCallback

callback = BotCallback(
    url=url,
    title=title)
```

3. Инициализировать бота:

```python
from vkbottle import Bot

bot = Bot(token=TOKEN, callback=callback)
```

4. Настроить любой сервер (`aiohttp`, `flask`, `fastapi`) и обрабатывать полученные события:

```python
# event - событие, полученное от vk
await bot.process_event(event)
```

> **Внимание.** После подключения бот будет обрабатывать входящие сообщения, для получения остальных событий необходимо включить их в настройках группы.

## Функции `Bot` для Callback API

- `bot.setup_webhook()` — устанавливает сервер для `CallbackAPI` в сообщество
- `bot.process_event(event)` — передает полученное событие в роутер, для его обработки

## Пример

- [Подключение CallbackAPI](https://github.com/vkbottle/vkbottle/blob/master/examples/high-level/callback_api/app.py)

---

# Работа с CallbackAPI (low-level)

Для поддержки `Callback API` реализован абстрактный класс `ABCCallback`, на основе которого вы можете сделать свою реализацию.

## Методы

| Метод | Описание |
|---|---|
| `add_callback_server` | Добавляет сервер в вашу группу вк |
| `delete_callback_server` | Удаляет сервер по `server_id` |
| `edit_callback_server` | Редактирует настройки существующего сервера по `server_id` |
| `get_callback_confirmation_code` | Получает код, необходимый для подтверждения вашего сервера |
| `get_callback_servers` | Получает список серверов, подключенных к сообществу |
| `get_callback_settings` | Получает список событий для указанного сервера по `server_id` |
| `set_callback_settings` | Устанавливает список событий для указанного сервера по `server_id` |
| `construct` | Принимает API, нужно для того чтобы конструировать поллинг с обновленным API при каждом вызове. Возвращает собственный инстанс, может быть использован в билдер интерфейсе |

## Параметры для `BotCallback`

- **`url`** — сервер, на который будут отправляться события
- **`title`** — короткое имя сервера, которое будет показываться в настройках сообщества
- **`secret_key`** — секретный ключ, по которому можно достоверно определить, что сообщение пришло именно от вашего бота. По умолчанию генерируется произвольная строка.
- **`api`** — если не указано, будет получен автоматически при создании объекта
- **`group_id`** — если не указано, будет автоматически получен при установке сервера

## Создание кастомного клиента

Ваша реализация должна наследоваться от `ABCCallback` и имплементировать вышеуказанные методы.

---

# Обработка callback-кнопок (MessageEvent)

Обработка `callback` кнопок выходит на новый уровень:

```python
from vkbottle import GroupEventType
from vkbottle.bot import MessageEvent


@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_message_event(event: MessageEvent):
    await event.show_snackbar("Сейчас я исчезну")
```

- Никакого `object`. Всё находится уже в `event`, вместе с `group_id`
- Поддержка всех генераторов `event-data` при помощи соответствующими функциями
- Поддержка рулзов, связанных с `payload`
- Так же есть `message_edit` и `message_send`

## Старый способ

```python
from vkbottle import GroupEventType, GroupTypes, ShowSnackbarEvent


@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=GroupTypes.MessageEvent)
async def handle_message_event(event: GroupTypes.MessageEvent):
    await event.ctx_api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
        event_data=ShowSnackbarEvent(text="Сейчас я исчезну").model_dump_json(),
    )
```

Полноценный пример: <https://github.com/vkbottle/vkbottle/tree/master/examples/high-level/callback_buttons.py>

---

Далее: [11. API, токены, HTTP-клиент](./11-api.md)
