# 06. Мидлвари (Middleware)

> Источники:
> - <https://vkbottle.readthedocs.io/ru/latest/tutorial/middlewares-return-managers/>
> - <https://vkbottle.readthedocs.io/ru/latest/high-level/handling/middleware/>

Мидлвари — так называемые внешние слои, покрывающие обработку хендлеров. У мидлварей есть два состояния — **`pre`** и **`post`**:

- `pre` — то, что происходит до начала поиска хендлера (когда только нашелся нужный `view`);
- `post` — то что происходит когда хендлер уже был обработан и известно все о прошедшей обработке: какие хендлеры сработали, что они вернули.

## Создание мидлваря

```python
from vkbottle import BaseMiddleware
from vkbottle.bot import Message


class MiddlewareName(BaseMiddleware[Message]):
    ...
```

Так как наш мидлварь обрабатывает именно сообщения, нужно указать тип в дженерике. В данном случае мы используем класс `Message` из `vkbottle.bot`.

Middleware без методов `pre` или/и `post` бесполезен.

### `async def pre(self)`

`pre` имеет доступ к ивенту (например сообщению) через `self` и может вернуть ошибку через `self.stop` или обновить контекст через `self.send`.

Вот так например можно отсеивать все сообщения от ботов:

```python
from vkbottle.bot import Message
from vkbottle import BaseMiddleware, MiddlewareResponse


class NoBotMiddleware(BaseMiddleware[Message]):
    async def pre(self):
        if self.event.from_id < 0:
            self.stop("from_id меньше 0")
```

### `async def post(self)`

`post` уже никак не может повлиять на обработку ивента. Обычно его используют для статистики и логов:

```python
from vkbottle.bot import Message
from vkbottle import BaseMiddleware


class LogMiddleware(BaseMiddleware[Message]):
    async def post(self):
        if not self.handlers:
            return
        print(f"{len(self.handlers)} хендлеров сработало на сообщение. "
              f"Они вернули {self.handle_responses}, "
              f"все они принадлежали к view {self.view}")
```

`pre` и `post` можно использовать и одновременно в одном мидлваре.

## Регистрация мидлварей

Чтобы зарегистрировать мидлварь (и он работал) нужно определиться с view к которому он принадлежит, в данном случае это `MessageView`.

В лейблере `MessageView` располагается по адресу `.message_view`.

У каждого view есть метод `register_middleware`:

```python
bot.labeler.message_view.register_middleware(NoBotMiddleware)
bot.labeler.message_view.register_middleware(LogMiddleware)
```

Кстати методом `register_middleware` можно пользоваться и как декоратором.

---

## Техническая документация по middleware

Мидлварь должен имплементировать методы `pre` и/или `post`. `pre` вызывается до поиска хендлеров, а `post` после. Мидлвари всегда распаковываются из `labeler`.

Абстрактный класс для мидлварей — `BaseMiddleware`. Конструктор принимает ивент в качестве аргумента.

`pre`/`post` **не принимают аргументов, должны возвращать `None`**:

- `self.stop(ошибка)` — исполнение view срочно останавливается
- `self.send({ключ: значение})` — в контекст добавляются аргументы (ключ — имя аргумента)

`BaseMiddleware` имеет доступ к следующим атрибутам:

| Атрибут | Описание |
|---|---|
| `event` | сам евент (тип указывается в дженерике) |
| `view: ABCView` | view, с которым был обработан ивент |
| `handle_responses: list` | все то что вернули хендлеры по порядку их исполнения |
| `handlers: list[ABCHandler]` | все хендлеры что были исполнены |

Тип ивента, который будет обрабатывать мидлварь, указывается в дженерике конструктора мидлвари:

```python
from vkbottle import BaseMiddleware
from vkbottle.bot import Message


class MyMiddleware(BaseMiddleware[Message]):
    ...
```

Для `message_view` это `Message`, а для `raw_event_view` — словарь.

Больше примеров: <https://github.com/vkbottle/vkbottle/tree/master/examples/high-level/middleware_example.py>

## Полный код с мидлварями

См. [middleware_example.py](https://github.com/vkbottle/vkbottle/tree/master/examples/high-level/middleware_example.py)

---

## Возвращаемые из хендлера значения (Return Manager)

См. подробно: [03-handlers.md — Return Manager](./03-handlers.md#return-manager)

| тип значения | что произойдет |
|---|---|
| `str` | строка отправится как сообщение |
| `tuple` или `list` | все элементы будут конвертированы в строки и отправлены как сообщения |
| `dict` | словарь распакуется как непозиционные аргументы для метода `message.answer` |

---

Далее: [07. Стейты](./07-states.md)
