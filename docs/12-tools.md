# 12. Прочие инструменты

> Источники:
> - <https://vkbottle.readthedocs.io/ru/latest/tools/loop-wrapper/>
> - <https://vkbottle.readthedocs.io/ru/latest/tools/formatting/>
> - <https://vkbottle.readthedocs.io/ru/latest/tools/storage/>
> - <https://vkbottle.readthedocs.io/ru/latest/tools/auth/>
> - <https://vkbottle.readthedocs.io/ru/latest/modules/>

Полный список инструментов: Auth Flows, Formatting, Keyboard, Loop Wrapper, Message Event, Storage, Template, Uploaders, VKScript, Waiter Machine.

- Клавиатура → [05-keyboards.md](./05-keyboards.md)
- Template → [05-keyboards.md](./05-keyboards.md)
- Uploaders → [05-keyboards.md](./05-keyboards.md)
- Message Event → [10-callback.md](./10-callback.md)
- Waiter Machine → [07-states.md](./07-states.md)
- VKScript → [11-api.md](./11-api.md)

---

# Loop Wrapper

`LoopWrapper` нужен чтобы контролировать ивент луп для работы с `asyncio` и хранить основные таски, `startup` и `shutdown`, которые будут исполнены только при запуске ивент лупа через `run_forever`.

## Таски

```python
from vkbottle import LoopWrapper


async def my_task():
    ...


lw = LoopWrapper()
lw.add_task(my_task())
lw.run()
```

## `on_startup` и `on_shutdown`

`on_startup` корутины запустятся перед запуском ивент лупа, `on_shutdown` при остановке. В экземпляре `LoopWrapper` они являются списками с корутинами:

```python
from vkbottle import LoopWrapper


async def startup_task():
    print("This is startup")


async def shutdown_task():
    print("This is shutdown")


lw = LoopWrapper()
lw.on_startup.append(startup_task())
lw.on_shutdown.append(shutdown_task())
lw.run()
```

## `interval`

Легкий темплейт для создания тасков с бесконечно повторяющимися действиями в интервале:

```python
from vkbottle import LoopWrapper

lw = LoopWrapper()


@lw.interval(seconds=10)
async def repeated_task():
    print("I'll print this every 10 seconds!")


lw.run()
```

## `timer`

Легкий темплейт для создания отложенного таска:

```python
from vkbottle import LoopWrapper

lw = LoopWrapper()


@lw.timer(seconds=10)
async def delayed_task():
    print("I'll print this after 10 seconds!")


lw.run()
```

> **Внимание.** Если вы используете `LoopWrapper` вместе с `Bot`, то учтите, то `Bot` уже имеет свой `LoopWrapper`, который доступен по пути `bot.loop_wrapper` и запускается при вызове `bot.run_forever()`.

---

# Formatting

Формирование форматированного текста осуществляется с помощью вспомогательного класса `Formatter`, который наследует класс `str` и имеет два перегруженных метода: `format`, `format_map`.

```python
from vkbottle.tools.formatting import Formatter
```

Доступные типы форматирования:

- `bold` — полужирный
- `italic` — курсив
- `url` — ссылка
- `underline` — подчеркнутый

> **Примечание.** Для типов форматирования специально реализованы такие же по названию функции, которые импортируются из модуля `vkbottle.tools.formatting`.

```python
Formatter("Hi, {}.").format("Alex")  # Hi, Alex.
Formatter("Hi, {name}.").format(name="Maria")  # Hi, Maria.
```

Метод также поддерживает специальные идентификаторы:

```python
Formatter("{:bold}, nice formatting!").format("Wow")  # Wow, nice formatting!
Formatter("{framework:italic} has been around for over 5 years!").format(framework="vkbottle")  # vkbottle has been around for over 5 years!
```

Для того, чтобы объединить типы форматов, используется синтаксис объединения через символ `+`:

```python
Formatter("Very cool {:bold+italic} ^_^").format("bold-italic message")  # Very cool bold-italic message ^_^
```

Метод `format_map` работает так же, как и `format`, за исключением того, что метод принимает один аргумент типа `Mapping`:

```python
Formatter("My bestie is {bestie:underline}").format_map({"bestie": "telegrinder"})  # My bestie is telegrinder
```

Объект `Formatter` имеет 2 свойства для того, чтобы получить форматирование в виде `json`:

- `format_data` — словарь `{"version": ..., "items": [...]}`.
- `raw_format_data` — сырой объект `format_data`.

> `format_data` необходим для методов, которые могут работать с форматированным текстом, например: `messages.send`.Подробнее в [документации VK API](https://dev.vk.ru/ru/reference/objects/message#format_data).

Класс `Format` необходим для представления типа форматирования, таких как: `bold`, `italic` и т. д. Класс поддерживает оператор `+=`, конкатенацию строк и самих типов-форматов:

```python
from vkbottle.tools.formatting import Format

bold("Hello, ") + italic("World!")  # Hello, World! ('Hello, ' is bold, 'World!' is italic)
"Hello, " + italic("World!")  # Hello, World! ('World!' is italic)
bold("Hello") + ", " + italic("World!")  # Hello, World! ('Hello' is bold, 'World!' is italic)
bold("vkbottle documentation:") + " " + url(italic("click me"), href="vkbottle.readthedocs.io/ru/latest")  # vkbottle documentation: click me ('click me' has an url)
```

`Format` имеет 2 метода для того, чтобы получить форматирование в виде `json`:

- `as_data` — словарь `{"version": ..., "items": [...]}`.
- `as_raw_data` — сырой объект `as_data`.

Пример использования с методом `BaseMessageMin.answer()`:

```python
await message.answer(Formatter("Hello, {:bold}!").format("World"))
await message.answer(underline(bold("Hello") + ", " + italic("World!")))
```

---

# Storage

Хранилища нужны чтобы хранить информацию в формате `ключ`: `значение`.

Все хранилища имеют такие методы:

- `get(key)`
- `set(key, value)`
- `delete(key)`
- `contains(key)`

## `CtxStorage`

Контекстное хранилище удобно тем что его можно открыть и изменить из любого места в коде, а главное оно доступно из-коробки. Пример: <https://github.com/vkbottle/vkbottle/tree/master/examples/low-level/ctx_storage_example.py>

## Создание своего хранилища

Если вы хотите создать свое хранилище например на основе `Rabbit MQ` вы можете это легко сделать:

- Наследуйтесь от `ABCStorage`.
- Имплементируйте методы `get`, `set`, `delete` и `contains` с подключением к `Rabbit MQ`.

---

# Auth Flows (`UserAuth`)

Это простой инструмент для быстрого получения токена пользователя по логину и паролю.

> **Warning.** Мы не несем ответственности за блокировку ваших аккаунтов ([см. подробнее](https://vkbottle.readthedocs.io/ru/latest/high-level/user/)).

```python
from vkbottle import UserAuth

login = "89012345678"
password = "qwerty123"


async def main():
    token = await UserAuth().get_token(login, password)
```

По умолчанию `UserAuth` использует для входа мобильное приложение вк. Вы можете указать другое приложение, передав `client_id` и `client_secret` в конструктор `UserAuth`.

По умолчанию токен запрашивается с определенным списком прав доступа. Для переопределения этого списка можно в методе `get_token` использовать параметр `scope`.

Пример получения токена с нужными правами:

```python
from vkbottle import UserAuth, UserPermission

login = "89012345678"
password = "qwerty123"


async def main():
    token = await UserAuth().get_token(login, password, scope=[UserPermission.photos, UserPermission.video])
```

### Основные права по умолчанию

| Права | По умолчанию |
|---|---|
| `UserPermission.friends` | ✓ |
| `UserPermission.photos` | ✓ |
| `UserPermission.audio` | ✗ |
| `UserPermission.video` | ✓ |
| `UserPermission.stories` | ✓ |
| `UserPermission.pages` | ✓ |
| `UserPermission.status` | ✓ |
| `UserPermission.notes` | ✓ |
| `UserPermission.messages` | ✗ |
| `UserPermission.wall` | ✓ |
| `UserPermission.offline` | ✓ |
| `UserPermission.docs` | ✓ |
| `UserPermission.groups` | ✓ |
| `UserPermission.market` | ✓ |
| `UserPermission.phone_number` | ✗ |

Полный список — в [официальной документации](https://vkbottle.readthedocs.io/ru/latest/tools/auth/).

При получении токена может потребоваться ввод капчи, либо дополнительное подтверждение через SMS или приложение для двухфакторной аутентификации (2FA). Пример с обработкой ошибок:

```python
from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, cast
from urllib.parse import parse_qs, urlparse

from vkbottle import APIAuthError, AuthError, CaptchaError, UserAuth

if TYPE_CHECKING:
    from typing import Optional, Union

login = "89012345678"
password = "qwerty123"


async def main():
    user_auth = UserAuth()
    auth_code: bool | str = True
    captcha_sid: str | None = None
    captcha_key: str | None = None
    while True:
        try:
            token = await user_auth.get_token(
                login,
                password,
                auth_code=auth_code,
                captcha_sid=captcha_sid,
                captcha_key=captcha_key
            )
            break
        except CaptchaError as error:
            captcha_sid = error.captcha_sid
            captcha_key = input(f"Open url '{error.captcha_img}' in browser and enter captcha code: ")
        except APIAuthError as error:
            if error.validation_type == "2fa_sms":
                validation_sid = cast(str, error.validation_sid)
                await user_auth.validate_phone(validation_sid)
                auth_code = input("Enter code from SMS: ")
                continue
            if error.validation_type == "2fa_app":
                print(f"Enter code from 2FA app here: {error.redirect_uri}")
                oauth_url = input("Enter OAuth URL from VK after signin in: ")
                parsed_url = urlparse(url=oauth_url)
                token = parse_qs(parsed_url.fragment)["access_token"][0]
                break
            print(error.error_description)
            return
        except AuthError as error:
            print(error.error_description)
            return

    print(f"Your token: {token}")


if __name__ == "__main__":
    asyncio.run(main())
```

---

# Кастомизация зависимостей

VKBottle автоматически выбирает лучшую альтернативу для стандартных библиотек. Эти библиотеки **не указаны в зависимостях**, поэтому вы должны установить их сами.

## JSON

В порядке убывания: `orjson`, `hyperjson`, `ujson`, `json`

## Logging

В порядке убывания: `loguru`, `logging`

> **Внимание.** Мы настоятельно рекомендуем использовать `loguru` вместо `logging`. Возможно, он станет обязательной зависимостью в будущих релизах.

> **Примечание.** По умолчанию уровень логирования выставлен на `DEBUG`. Изменить это вы можете так:

С `logging`:

```python
import logging

logging.getLogger("vkbottle").setLevel(logging.INFO)
```

С `loguru` (установить определенный уровень):

```python
import sys

from loguru import logger

logger.remove()
logger.add(sys.stderr, level="INFO")
```

Или установить переменную окружения `LOGURU_LEVEL`.

Отключить логирование полностью:

```python
from loguru import logger

logger.disable("vkbottle")
```

---

Далее: [13. FAQ](./13-faq.md)
