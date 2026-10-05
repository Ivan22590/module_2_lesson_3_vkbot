# Документация VKBottle (локальная копия)

Локальная выжимка официальной документации **VKBottle** — фреймворка для работы с VK API и создания ботов.

- Источник: <https://vkbottle.readthedocs.io/ru/latest/>
- Дата сканирования: 05.10.2026
- Все примеры кода взяты **дословно** с сайта документации / официального README.

## Установка

Из официального README (<https://github.com/vkbottle/vkbottle>):

```console
pip install vkbottle
```

## Hello World

```python
from vkbottle.bot import Bot

bot = Bot("GroupToken")


@bot.on.message()
async def handler(_) -> str:
    return "Hello, World!"


bot.run()
```

## Оглавление

| Файл | Тема | Источник на сайте |
|---|---|---|
| [01-first-bot.md](01-first-bot.md) | Первый бот, работа с `API`, `Bot`, декораторы | `tutorial/first-bot/` |
| [02-rules.md](02-rules.md) | Правила (rules), все встроенные правила, свои правила | `tutorial/rules/`, `high-level/builtin-rules/`, `high-level/handling/rules/` |
| [03-handlers.md](03-handlers.md) | Хендлеры, View, Router, Return Manager | `high-level/handling/*` |
| [04-code-separation.md](04-code-separation.md) | Разделение кода, Labeler | `tutorial/code-separation/`, `high-level/bot/labeler/` |
| [05-keyboards.md](05-keyboards.md) | Клавиатуры, вложения, шаблоны-карусели, загрузчики | `tutorial/keyboards-attachments/`, `tools/keyboard/`, `tools/uploaders/`, `tools/template/` |
| [06-middleware.md](06-middleware.md) | Мидлвари | `tutorial/middlewares-return-managers/`, `high-level/handling/middleware/` |
| [07-states.md](07-states.md) | Стейты: State Dispenser и Waiter Machine | `high-level/handling/state-dispenser/`, `tools/waiter-machine/` |
| [08-errors.md](08-errors.md) | Обработка ошибок API и исключений | `tutorial/error-handling/`, `low-level/exception_handling/*` |
| [09-longpoll.md](09-longpoll.md) | **LongPoll API** — запуск, параметры, мультибот | `low-level/polling/`, `high-level/bot/` |
| [10-callback.md](10-callback.md) | Callback API, webhook, callback-кнопки | `tutorial/callback-bot/`, `low-level/callback/`, `tools/message-event/` |
| [11-api.md](11-api.md) | API, токены и генераторы токенов, HTTP-клиент, vkscript | `low-level/api/*`, `low-level/http-client/`, `tools/vkscript/` |
| [12-tools.md](12-tools.md) | Loop Wrapper, Formatting, Storage, Auth, мультибот | `tools/*`, `high-level/bot/multibot/` |
| [13-faq.md](13-faq.md) | FAQ: asyncio, типизация, токены, нестандартные методы | `tutorial/faq/` |

## Карта разделов официальной документации

- **Туториал** — `tutorial/`: first-bot, rules, code-separation, keyboards-attachments, middlewares-return-managers, error-handling, callback-bot, recommended-ide, faq
- **High-level** — `high-level/`:
  - Бот: Bot, User, Labeler, Blueprint (устарел), Multibot
  - Хендлинг: Handler, View, Router, Return Manager, State Dispenser, Middleware, Rules
  - Builtin Rules
- **Low-level** — `low-level/`:
  - API: Accessing API, Response Validator, Request Rescheduler, Request Validators, Token Generators
  - Exception Handling: Error Handler, Code Exception
  - Http Client
  - **Polling (LongPoll)**
  - Callback
- **Tools** — `tools/`: Auth Flows, Formatting, Keyboard, Loop Wrapper, Message Event, Storage, Template, Uploaders, VKScript, Waiter Machine
- **Кастомизация зависимостей** — `modules/`
- **Чейнджлог** — `whats_new/` (4.0, 4.1, 4.2, 4.3)

## Главные предупреждения с сайта

1. **`Bot` — класс исключительно для групп.** Для юзербота см. `high-level/user/`, но использование юзерботов запрещено несколькими правилами ВКонтакте (п. 6.3.9, 6.7) — фреймворк не несёт ответственности за блокировки.
2. **Все встроенные rules и middlewares работают только с объектами `Message` и `MessageEvent` из `vkbottle.bot`** (для сырых евентов нужна своя реализация).
3. **Blueprint`ы устарели** и будут удалены — используй разделение кода через `BotLabeler` + `labeler.load()`.
4. **Все методы VK API во фреймворке пишутся в `snake_case`** (`messages.getById` → `api.messages.get_by_id`).
5. **Только асинхронные библиотеки**: `asyncio.sleep()` вместо `time.sleep()`, `aiohttp`/`AiohttpClient` вместо `requests`.
6. Для LongPoll в настройках группы должны быть отмечены нужные события, стабильная версия API — **5.131**.
