# 11. API, токены, HTTP-клиент, vkscript

> Источники:
> - <https://vkbottle.readthedocs.io/ru/latest/low-level/api/>
> - <https://vkbottle.readthedocs.io/ru/latest/low-level/api/token-generator/>
> - <https://vkbottle.readthedocs.io/ru/latest/low-level/http-client/>
> - <https://vkbottle.readthedocs.io/ru/latest/tools/vkscript/>

---

# API

Вы можете взаимодействовать с API ВКонтакте прямо из коробки:

```python
from vkbottle import API

# ...
api = API(token="token")
await api.messages.send(peer_id=1, message="Привет Павел Дуров!")
```

> **Внимание.** Все методы в vkbottle пишутся *снейк_кейсом*. Это значит, например, что метод [`messages.getById`](https://dev.vk.ru/method/messages.getById) в vkbottle пишется как `api.messages.get_by_id`.

## Параметры

- **`token`** — токен сообщества/пользователя или генератор токенов
- **`ignore_error`** — игнорировать ошибки VK API
- **`http_client`** — клиент для запросов ([документация](#http-client))
- **`request_rescheduler`** — рещедулер запросов

## Captcha хендлер

Должен решить капчу и вернуть ее код:

```python
from vkbottle import CaptchaError

bot = ...


async def captcha_handler(e: CaptchaError):
    ...
    return code


bot.api.add_captcha_handler(captcha_handler)
```

---

# Token-Generator

У VK существуют лимиты на запросы, но эти лимиты легко обходятся при наличии нескольких токенов, для того чтобы автоматически распределять токены на каждый запрос используются токен генераторы. Существует 2 вида генераторов из коробки:

- **`SingleTokenGenerator`** — используется один токен на все запросы, принимает строку
- **`ConsistentTokenGenerator`** — используется несколько токенов поочередно, если вы хотите его использовать грамотно, необходимо рассчитать нагрузку по времени

**Лимит ВКонтакте на запросы:**
- для ботов — **25/сек**
- для пользователей — **3/сек**

По правилам vkbottle вы конечно же можете реализовать свой генератор, базируясь на интерфейсе [ABCTokenGenerator](https://github.com/vkbottle/vkbottle/blob/master/vkbottle/api/token_generator/abc.py).

> Лист строк (токенов), переданный в `API`, автоматически конвертируется в токен-генератор.

---

# HTTP-Client

По-умолчанию библиотека использует `SingleAiohttpClient` для отправки всех запросов. (Его особенность в том, что он всегда использует одну и ту же сессию.)

## Методы

| Метод | Описание |
|---|---|
| `request_raw` | Делает реквест. Для aiohttp возвращает объект `aiohttp.ClientResponse` |
| `request_text` | Делает реквест и читает поле `text`. Возвращает строковый тип |
| `request_json` | Делает реквест и десериализует `json` (см. порядок библиотек ниже). Возвращает словарь |
| `request_content` | Делает реквест и читает вернувшийся `content`, используется для скачивания медиафайлов в аплоадерах. Возвращает байты |

`request_json` выбирает модуль десериализации с помощью `choicelib` в порядке слева направо: `json`, `ujson`, `hyperjson`, `orjson`.

## Параметры

- `url` — ссылка по которой будет произведен
- `method` — HTTP метод запроса (например: `get`)
- `data` — данные которые будут переданы в запросе
- `**kwargs` — передаются в качестве параметров в запросе

### При инициализации `AiohttpClient` можно указать параметры

- `session` — объект сессии (если не указан, то будет создан новый)
- `json_processing_module` — модуль для десериализации json
- `optimize` — если передан `True`, то в конструктор сессии будут переданы параметры `raise_for_status=True` и `skip_auto_headers={"User-Agent"}`
- `**session_params` — `**kwargs`, передаются в конструктор сессии. Можно использовать для передачи `headers` или `cookies`

Подробнее о параметрах сессии: <https://docs.aiohttp.org/en/stable/client_reference.html>

## Пример

```python
from vkbottle.http import AiohttpClient

# ...
http_client = AiohttpClient()
await http_client.request_text("https://google.com")
```

## Создание кастомного клиента

Кастомный клиент должен унаследовать `ABCHTTPClient` и имплементировать вышеупомянутые методы.

---

# Нестандартные методы API

> Источник: <https://vkbottle.readthedocs.io/ru/latest/tutorial/faq/>

Если очень нужно использовать то, чего во фреймворке и официальной документации нет, используйте `API.request`, `Bot.api.request` или `Message.ctx_api.request` методы.

**После их выполнения вернёт словарь с json ответом, а не типизированный объект, учитывайте это.**

```python
import asyncio

from vkbottle.api import API

api = API("token")


async def main():
    await api.request("users.get", {})  # Single request
    # Multiple request for one session
    async for response in api.request_many(
        [api.APIRequest("users.get", {}), api.APIRequest("groups.get", {})]
    ):
        print(response)


asyncio.run(main())
```

Для бота необходимо инициализировать класс **Bot**. В нём присутствует класс **API**, его дополнительно инициализировать не надо:

```python
import asyncio

from vkbottle.bot import Bot

bot = Bot("token")


async def main():
    print(await bot.api.request("users.get", {}))  # Single request
    # Multiple request for one session
    async for response in bot.api.request_many(
        [bot.api.APIRequest("users.get", {}), bot.api.APIRequest("groups.get", {})]
    ):
        print(response)


asyncio.run(main())
```

Также доступ к классу **API** можно получить через объект `Message` с помощью параметра `Message.ctx_api`:

```python
from vkbottle.bot import Bot, Message

bot = Bot(token="token")
admin_ids = [1, 100]


@bot.on.message(text="админы")
async def who_admins(message: Message):
    admins = [f"{adm.first_name} {adm.last_name}" for adm in (await message.ctx_api.users.get(admin_ids))]
    print((await message.ctx_api.request("users.get", {"user_ids": admin_ids})))
    await message.answer(f"Администраторы этого бота: {' '.join(admins)}")


bot.run_forever()
```

---

# VKScript Converter

Просто импортируйте `vkscript` из библиотеки и напишите функцию, которая будет работать с api для того, обернув в декоратор, чтобы после ее вызова вам вернулся код выполняющий логику вашей функции, но в `VKScript`:

```python
from vkbottle import vkscript


@vkscript
def my_execute(api, user_ids=()):
    message_ids = []
    for user_id in user_ids:
        user = api.users.get(user_ids=user_id)[0]
        message_ids.append(api.messages.send(message=f"{user.first_name}, спасибо что зашел на чай", random_id=0, peer_id=user_id))
    return message_ids


# далее вызывая эту функцию вы можете использовать ее ответ в качестве кода для execute
await api.execute(code=my_execute(user_ids=[10, 11, 12]))
```

---

Далее: [12. Прочие инструменты](./12-tools.md)
