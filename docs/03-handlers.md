# 03. Хендлеры, View, Router, Return Manager

> Источники:
> - <https://vkbottle.readthedocs.io/ru/latest/high-level/handling/handler/>
> - <https://vkbottle.readthedocs.io/ru/latest/high-level/handling/router/>
> - <https://vkbottle.readthedocs.io/ru/latest/high-level/handling/view/>
> - <https://vkbottle.readthedocs.io/ru/latest/high-level/handling/return-manager/>
> - <https://vkbottle.readthedocs.io/ru/latest/high-level/bot/>

## Хендлеры (Handler)

Хендлеры это конечная точка в обработке событий. Хендлеры могут быть **блокирующими** (если нашелся подходящий хендлер другие уже не проверяются и не выполняются) и **не блокирующими** (в таком случае количество выполняемых хендлеров не ограничено и зависит от того какие пройдут). По умолчанию все хендлеры являются блокирующими.

Хендлеры помечаются (лейблируются) с помощью декораторов. За это отвечает `Labeler` high-level инстанс.

Пример с ботом:

```python
from vkbottle.bot import Bot, Message

bot = Bot("token")


@bot.on.message()
async def any_message(message: Message):
    await message.answer("Привет я бот")


bot.run_forever()
```

### Хендлеры ботов

| Декоратор | Описание |
|---|---|
| `message` | Хендлер на все сообщения (и из чата, и из личных сообщений) |
| `chat_message` | Хендлер на сообщения из чатов |
| `private_message` | Хендлер на сообщения из личных диалогов |

> **Примечание.** Типы хендлеров выше не делают ничего необычного, просто оперируют предустановленным правилом `PeerRule`:
> - в `message` он не предустанавливается;
> - в `chat_message` — `PeerRule(True)`;
> - в `private_message` — `PeerRule(False)`.

В качестве аргументов декоратор принимает инстансы правил (`ABCRule`), а в качестве `kwargs` он принимает значение из `custom_rules` (см. [02-rules.md](./02-rules.md)).

---

## Роутер (Router)

Роутер — компонент, который принимает запрос и передает его в подходящий view. Также роутер передает ошибки, которые возникают во время выполнения `view`.

Атрибуты роутера:

- `views` — словарь с view, которые будут обрабатываться роутером
- `state_dispenser` — компонент, который отвечает за хранение состояний ([документация](./07-states.md))
- `error_handler` — компонент, который отвечает за обработку ошибок ([документация](./08-errors.md))

Методы роутера:

- `route` — метод, который принимает событие и контекст `API` и передает его в подходящий `view`
- `construct` — метод, который принимает атрибуты роутера и устанавливает их
- `add_view` — метод, который принимает имя `view` и сам `view` и добавляет его в словарь `views`
- `view` — декоратор, который принимает имя `view` и сам `view` и добавляет его в словарь `views`

---

## View (Handling-View)

View являются **блокирующими менеджерами хендлеров**. Если `process_event` у view вернул `True` то другие view уже не будут проверяться.

Процедура поиска view обрабатывающего ивент проста:

Сначала обрабатывается `process_view` который должен вернуть boolean-значение. Если вернулось `True` то поиск view прекращается и вызывается `handle_event` который отвечает за подбор хендлера.

### `register_middleware(BaseMiddleware)`

Добавляет мидлварь в `view.middlewares`.

### Написание своего view

> **Примечание.** View — это "большой хендлер", имплементирующий индивидуальную логику работы с мидлварями, стейт менеджером и производными хендлеров. Кастомные view нужны обычно для создания среды обработки какого-то ивента или группы ивентов.

Пример view для сообщений: <https://github.com/vkbottle/vkbottle/blob/master/vkbottle/dispatch/views/bot/message.py>

У каждого view существует минимум **4** атрибута:

- `handlers` — лист из `ABCHandler`
- `middlewares` — сет из классов `BaseMiddleware`
- `middleware_instances` — лист объектов `BaseMiddleware`, используется в `view.pre_middleware` и `view.post_middleware`
- `handler_return_manager` — `BaseReturnManager`

Из них **рекомендуются** 2 атрибута: `handlers` и `middlewares`.

```python
from vkbottle import ABCView, MiddlewareResponse
from vkbottle_types.events.bot_events import PollVoteNew


class VoteView(ABCView):
    def __init__(self):
        super().__init__()

    async def process_event(self, event: dict[str, Any]) -> bool:
        # Эта функция принимает ивент в форме словаря,
        # она должна определить подходит ли ивент под
        # текущий view или нет и вернуть соответствующее
        # boolean-значение
        return event["type"] == "poll_vote_new"

    async def handle_event(
        self, event: dict, ctx_api: "ABCAPI", state_dispenser: "ABCStateDispenser"
    ):
        # Эта функция полностью обрабатывает
        # полученный ивент
        vote = PollVoteNew(**event)
        # Здесь можно обозначить стейт-каст
        # по определенному ключу для объекта
        vote.object.state_peer = await state_dispenser.cast(vote.object.user_id)
        # Здесь можно имплементировать стандартное поведение мидлварей
        # Например, если `pre_middleware` вернул что-либо, то в одном из
        # мидлварей был вызван `self.stop(...)` - обработка сразу останавливается
        mw_instances = await self.pre_middleware(vote)
        if mw_instances is None:
            return logger.info("Обработка остановлена, pre_middleware вернул ошибку")
        # `handlers` и `handle_responses` нужны для post мидлварей
        handlers = []
        handler_responses = []
        context = dict()
        for handler in self.handlers:
            if not await handler.filter(vote, context):
                continue
            handler_responses.append(await handler.handle(vote, **context))
            handlers.append(handler)
            if handler.blocking:
                break
        # Запуск post-мидлварей
        await self.post_middleware(mw_instances, handler_responses, handlers)
```

Регистрация хендлеров через `FromFuncHandler`:

```python
from vkbottle.bot import Bot, rules, BotLabeler
from vkbottle.dispatch.handlers import FromFuncHandler
from vkbottle_types.events.bot_events import PollVoteNew


async def vote_up(vote: PollVoteNew):
    print(
        "{} со стейтом {} голосует за {}".format(
            vote.object.user_id, vote.object.state_peer, vote.object.option_id
        )
    )


async def vote_up_admin(vote: PollVoteNew):
    print("Админ проголосовал за {}", vote.object.option_id)


my_view = VoteView()
my_view.handlers = [
    FromFuncHandler(
        vote_up_admin,
        rules.FuncRule(lambda v: v.object.user_id in admin_ids),
    ),
    FromFuncHandler(vote_up),
]


class MyLabeler(BotLabeler):
    def views(self) -> dict[str, "ABCView"]:
        # Из views должны быть возвращены все view которые
        # будут позже обрабатываться роутером
        return {"vote_view": my_view}


bot = Bot()
bot.labeler = MyLabeler()
admin_ids = [1]
```

Бот с `VoteView` готов.

---

## Return Manager

Для каждого view можно установить `handler_return_manager`. Этот менеджер будет обрабатывать то, что возвращается из хендлеров. По умолчанию менеджеры предустановлены в некоторых `view`.

| тип значения | что произойдет |
|---|---|
| `str` | строка отправится как сообщение |
| `tuple` или `list` | все элементы будут конвертированы в строки и отправлены как сообщения |
| `dict` | словарь распакуется как непозиционные аргументы для метода `message.answer` |

Реализация для сообщений:

```python
from vkbottle import BaseReturnManager
from vkbottle.bot import Message
from typing import Union


class BotMessageReturnHandler(BaseReturnManager):
    @BaseReturnManager.instance_of(str)
    async def str_handler(self, value: str, message: Message, _: dict[str, Any]):
        await message.answer(value)

    @BaseReturnManager.instance_of((tuple, list))
    async def iter_handler(self, value: tuple | list, message: Message, _: dict[str, Any]):
        [await message.answer(str(e)) for e in value]

    @BaseReturnManager.instance_of(dict)
    async def dict_handler(self, value: dict, message: Message, _: dict[str, Any]):
        await message.answer(**value)
```

Первым аргументов в хендлер приходит само значение, что было получено из хендлера, вторым — объект ивента, третьим — данные из рулзов и мидлварей.

Хендлеры оборачиваются в декоратор `instance_of`, который принимает в качестве единственного аргумента тип или кортеж типов.

---

## Bot: атрибуты и функции

> Источник: <https://vkbottle.readthedocs.io/ru/latest/high-level/bot/>

Инстанс бота состоит из стандартного апи, лонгпола и других частей фреймворка.

### Атрибуты

| Атрибут | Назначение |
|---|---|
| `bot.api` | [API документация](./11-api.md) |
| `bot.router` | Router документация (этот файл) |
| `bot.labeler` / `bot.on` | [Labeler документация](./04-code-separation.md) |
| `bot.polling` | [Polling документация](./09-longpoll.md) |
| `bot.callback` | [Callback документация](./10-callback.md) |
| `bot.error_handler` | [Error handler документация](./08-errors.md) |
| `bot.loop_wrapper` | [Loop Wrapper документация](./12-tools.md) |

### Long Poll API

- **`bot.run_polling()`** — асинхронный запуск longpoll
- **`bot.run_forever()`** — синхронный запуск longpoll. Добавляет `run_polling` в таски `bot.loop_wrapper` и вызывает `bot.loop_wrapper.run()`

### Callback API

- **`bot.setup_webhook()`** — устанавливает сервер для `CallbackAPI` в сообщество
- **`bot.process_event(event)`** — передает полученное событие в роутер, для его обработки

---

Далее: [04. Разделение кода и Labeler](./04-code-separation.md)
