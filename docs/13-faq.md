# 13. FAQ

> Источник: <https://vkbottle.readthedocs.io/ru/latest/tutorial/faq/>

---

## Asyncio

### Что такое coroutine?

Coroutine это функция (сопрограмма), которая должна вызываться через **await**.

Когда в Python выполнение кода доходит до **await**, он останавливает выполнение в этой функции, и вернётся к ней, пока не выполнит другие сопрограммы и не завершит работу этой функции.

Благодаря такому подходу, программа может выполнять конкурентно несколько задач одновременно без использования потоков, а следовательно, будет экономия ресурсов железа и высокая производительность.

### Не забывайте перед async функцией писать вначале await, иначе она не запустится

```python
import asyncio


async def get_banana() -> str:
    return "banana"


async def main():
    print(get_banana())  # <coroutine object get_banana at 0x...>
    print(await get_banana())  # banana


asyncio.run(main())
```

### Где надо писать `await`?

Надо `await` писать только внутри **async** функций и больше нигде.

```python
# bad
async def foo() -> str:
    return "foo"


def main():
    print(await foo())  # SyntaxError: 'await' outside async function


main()
```

```python
# bad
async def main():
    print("main")

await main()  # SyntaxError: 'await' outside function
```

```python
# good
import asyncio


async def foo() -> str:
    return "foo"


async def main():
    print(await foo())


asyncio.run(main())
```

### Как происходит "блокировка" функции?

В асинхронном программировании блокирующие функции это все функции без конструкции **await**, работающие на принципе IO (Input/Output).

Но не все блокирующие функции плохи, так как их использование неизбежно. Главное этим не злоупотреблять. Если заблокируете выполнение функции надолго, то ваш бот зависнет, потому что он не остановил функцию в нужный момент, чтобы выполнять другие сопрограммы.

Самые частые проблемы блокировок происходят из-за функций типа `time.sleep()`. В **async** функциях используйте `asyncio.sleep()`.

```python
# bad
time.sleep(10)
```

```python
# good
await asyncio.sleep(10)
```

Также распространённой проблемой долгой блокировки является модуль **requests**, **urllib3** и ему производные API-обёртки (**vk_api**, и тп). Они хороши для **неасинхронного** программирования, но могут произойти ситуации, когда запрос и ответ с сервера может идти долго и бот из-за этого зависнет. Используйте для этого модуль [aiohttp](https://docs.aiohttp.org/en/stable/client_quickstart.html), он идет зависимостью в vkbottle, или используйте встроенный `AiohttpClient`.

```python
# bad
async def send_httpbin_get() -> dict[str, Any]:
    r = requests.get('http://httpbin.org/get')
    if r.status_code == 200:
        js = r.model_dump_json()
        return js
```

```python
# good, recommended
# see https://vkbottle.rtfd.io/ru/latest/low-level/http-client/
from vkbottle.http import AiohttpClient


async def send_httpbin_get() -> dict[str, Any]:
    http_client = AiohttpClient()
    return await http_client.request_json('http://httpbin.org/get')
```

```python
# good
import aiohttp


async def send_httpbin_get() -> dict[str, Any]:
    async with aiohttp.ClientSession() as session:
        async with session.get('http://httpbin.org/get') as r:
            if r.status == 200:
                js = await r.json()
                return js
```

### Почему так мало базы? Ничего не понятно

В Python написание async кода требует такого же освоения и понимания, как и других синтаксических конструкций. Подробнее о работе с asyncio читайте в [официальной документации](https://docs.python.org/3/library/asyncio.html).

---

## Какие методы присутствуют во фреймворке

Всё что есть в [официальной документации от vk.ru](https://dev.vk.ru/reference).

Синтаксис методов, параметры и ошибки аналогичны документации выше, только методы пишутся в **snake_case**, а не **camelCase**.

```python
from vkbottle.api import API

api = API("token")

# https://api.vk.ru/method/account.ban
await api.account.ban(owner_id=1)

# https://api.vk.ru/method/account.getBanned
await api.account.get_banned(offset=0, count=1)
```

Все официальные методы, ответы и ошибки в этом фреймворке **типизированы**. Чтобы не гадать, перебирать и постоянно заглядывать в документацию, поставьте настоящий редактор кода, чтобы он давал подсказки. А также настоятельно рекомендуется по ходу написания кода использовать тайпхинты.

---

## Как получить токен для пользователя

Самый простой способ воспользоваться сервисом [vkhost.github.io](https://vkhost.github.io)

## Как получить токен для бота

У бота (токена от сообщества) не все методы доступны в отличие от получения токена через пользователя, учитывайте это. [Чат бот Быстрый старт](https://dev.vk.ru/api/bots/getting-started)

---

## Как отправить метод, которого нет во фреймворке

См. подробно: [11-api.md — Нестандартные методы API](./11-api.md#нестандартные-методы-api)

Используйте `API.request`, `Bot.api.request` или `Message.ctx_api.request` методы. После их выполнения вернёт словарь с json ответом, а не типизированный объект.

---

## `Pydantic.error_wrappers.ValidationError`

Объекты в этом фреймворке типизированы и генерируются на основе [официальной VK-API схемы](https://github.com/VKCOM/vk-api-schema).

Они её обновляют без предупреждений и из-за этого могут произойти поломки с валидацией объектов.

Если эта ошибка произошла, попробуйте обновить типы:

```
pip install git+https://github.com/vkbottle/types -U
```

Если и это не помогло, пишите issue (**в vkbottle, не types**) или в чат ВК/Телеграмм.

---

## Рекомендуемые IDE

Раздел официальной документации: <https://vkbottle.readthedocs.io/ru/latest/tutorial/recommended-ide/>

---

Далее: [01. Первый бот](./01-first-bot.md) · [Все разделы](./README.md)
