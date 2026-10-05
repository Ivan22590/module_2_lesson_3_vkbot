# 08. Обработка ошибок

> Источники:
> - <https://vkbottle.readthedocs.io/ru/latest/tutorial/error-handling/>
> - <https://vkbottle.readthedocs.io/ru/latest/low-level/exception_handling/error-handler/>
> - <https://vkbottle.readthedocs.io/ru/latest/low-level/exception_handling/code-exception/>

Иногда при запросах к api вконтакте возникают ошибки, для их обработки во фреймворке предусмотрено несколько инструментов.

## `try ... except VKAPIError`

`VKAPIError` — подтип `CodeException`, особенность которого заключается в том, чтобы ошибка идентифицировалась в `except` и без указанного кода (`except VKAPIError`) и при указании кода (`except VKAPIError[code]`).

В `VKAPIError` есть два поля:

- `code` — код ошибки, `int`
- `error_msg` — описание ошибки, `str`

```python
from vkbottle import VKAPIError

try:
    await api.wall.post()
except VKAPIError as e:
    print("Возникла ошибка", e.code)
```

При исполнении этого кода vk вернет ошибку, из-за того что не были переданы нужные параметры.

## `try ... except VKAPIError[code]`

Кроме более общего способа для обработки всех ошибок vk в одном блоке `except`, вы можете воспользоваться более конкретным `VKAPIError[code]`.

> **Примечание.** Список всех ошибок с их кодами можно найти [здесь](https://dev.vk.ru/reference/errors).

```python
try:
    await api.messages.send(peer_id=1, message="привет!", random_id=0)
except VKAPIError[902] as e:
    print("не могу отправить сообщение из-за настроек приватности")
except VKAPIError as e:
    print("не могу отправить:", e.error_msg)
```

## Специфичные ошибки

Некоторые ошибки vk имеют дополнительные поля:

- `CaptchaError`:
  - `captcha_sid` — идентификатор captcha, `str`
  - `captcha_img` — ссылка на изображение, `str`

---

# ErrorHandler

> Источник: <https://vkbottle.readthedocs.io/ru/latest/low-level/exception_handling/error-handler/>

Хендлер ошибок нужен для быстрой и простой обработки любых типов исключений.

```python
from vkbottle import ErrorHandler

error_handler = ErrorHandler(redirect_arguments=False, raise_exceptions=False)
# Если redirect_arguments = True, то все аргументы обернутой функции будут поступать и в хендлер исключения
# Если raise_exceptions = True, то все необработанные исключения будут выброшены (игнорируется, если есть обработчик для ненайденных ошибок)


@error_handler.register_error_handler(RuntimeError)
async def exc_handler_runtime(e: RuntimeError):
    print("Oh no runtime error occurred:", e)


@error_handler.register_error_handler(LookupError)
async def exc_handler_lookup(e: LookupError):
    print("Oh no lookup error occurred:", e)
```

Хендлер для ненайденных ошибок:

```python
@error_handler.register_undefined_error_handler
async def exc_handler_undefined(e: Exception):
    print("Oh no unknown error occurred", e)
```

Чтобы error_handler сработал на вашей асинхронной функции, добавьте к ней декоратор:

```python
@error_handler.catch
async def main():
    raise LookupError("I ve lost my keys")
```

Запустите её:

```python
import asyncio

asyncio.run(main())
```

Вывод:

```
Oh no lookup error occurred: I've lost my keys
```

## Методы `ErrorHandler`

- `register_error_handler` — декоратор, принимающий типы ошибок и асинхронную функцию-хендлер. Если возникнет одна из указанных ошибок (или её подтипа), исполнится указанный хендлер.
- `register_undefined_error_handler` — декоратор, принимающий тип ошибки и асинхронную функцию-хендлер. Если возникнет неизвестная ошибка, исполнится этот хендлер.
- `handle` — принимает экземпляр ошибки. Передаёт ошибку в соответствующий хендлер, зарегистрированный с помощью вышеописанных декораторов. Если для данной ошибки нет хендлера, поднимает её.
- `catch` — декоратор. Ловит ошибки из декорированной функции и передаёт их методу `handle`.

## Регистрация хендлеров ошибок с ботом

```python
from vkbottle import Bot, VKAPIError

bot = Bot("token")


@bot.error_handler.register_error_handler(RuntimeError)
async def runtime_error_handler(e: RuntimeError):
    print("возникла ошибка runtime", e)


@bot.error_handler.register_error_handler(VKAPIError[902])
async def unable_to_write_handler(e: VKAPIError):
    print("человек не разрешил отправлять сообщения", e)
```

Регистрация хендлеров сразу для нескольких типов ошибок:

```python
from typing import Union

from vkbottle import Bot, VKAPIError

bot = Bot("token")


@bot.error_handler.register_error_handler(TypeError, ValueError)
async def type_or_value_error_handler(e: TypeError | ValueError):
    print("возникла ошибка type или value", e)


@bot.error_handler.register_error_handler(*VKAPIError[6, 9])
async def limit_reached_write_handler(e: VKAPIError):
    print("ой, слишком много запросов", e)
```

Ещё у `ErrorHandler` есть параметр `redirect_arguments: bool`, который позволяет передавать в хендлер аргументы из задекорированной с помощью `catch` функции. В связке с ботом позволяет передать в хендлер контекстные аргументы из правил и мидлварей.

## Captcha хендлер

> Источник: <https://vkbottle.readthedocs.io/ru/latest/low-level/api/>

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

# Code-Exception

Базовый класс для исключений с кодом — `CodeException`. У `CodeException` generic-подобный синтаксис, код ошибки указывается в `[квадратных скобках]`. Базовое Исключение для ошибок API можно импортировать под именем `VKAPIError`.

```python
class MyCodeError(CodeException):
    pass


try:
    raise MyCodeError[1]("Error description")
except MyCodeError[1]:
    print("Error with code 1 appeared")
except MyCodeError[2, 3]:
    print("Error with code 2 or 3 appeared")
except MyCodeError as e:  # Ошибка с любым кодом
    print(f"Error with code {e.code} appeared")
```

---

Далее: [09. LongPoll API](./09-longpoll.md)
