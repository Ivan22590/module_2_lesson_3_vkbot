# 09. Long Poll API (Polling)

> Источники:
> - <https://vkbottle.readthedocs.io/ru/latest/low-level/polling/> — основной раздел про LongPoll
> - <https://vkbottle.readthedocs.io/ru/latest/high-level/bot/> — запуск у `Bot`
> - <https://vkbottle.readthedocs.io/ru/latest/high-level/bot/multibot/> — несколько лонгполов

---

## Как устроен LongPoll во фреймворке

Библиотека использует `Polling`, чтобы реализовывать longpoll. **Для ботов и юзеров создан соответствующий поллинг** (так как они разные):

- `BotPolling` — для ботов (Bot Long Poll API)
- `UserPolling` — для юзеров (User Long Poll API)

Вы можете написать свой поллинг, базируясь на абстрактном `ABCPolling`.

---

## Работа с поллингом

### `get_server`

Получает сервер для поллинга и возвращает его.

### `get_event`

Получает сервер из `get_server` в параметр и делает долгий POST реквест.

### `listen`

Асинхронный итератор (будет использован с `async with`). Генерирует приходящие ивенты.

### `construct`

Принимает API, нужно для того чтобы конструировать поллинг с обновленным API при каждом вызове. Возвращает собственный инстанс, может быть использован в билдер интерфейсе.

---

## Стандартные параметры для `BotPolling` / `UserPolling`

| Параметр | Описание |
|---|---|
| `api` | если не указано будет получено в `listen` |
| `group_id` / `user_id` | если не указано будет получено в `listen` |
| `wait` | лимит секунд после которого вк будет принудительно возвращает ответ на долгий реквест (даже если нет обновлений) |
| `rps_delay` | если не указано задержка равна 0 |

---

## Создание кастомного поллинга

Кастомный поллинг должен унаследовать `ABCPolling` и имплементировать вышеупомянутые методы (`get_server`, `get_event`, `listen`, `construct`).

---

# Запуск LongPoll через `Bot`

> Источник: <https://vkbottle.readthedocs.io/ru/latest/high-level/bot/>

### `bot.run_polling()`

Асинхронный запуск longpoll.

### `bot.run_forever()`

Синхронный запуск longpoll. Добавляет `run_polling` в таски `bot.loop_wrapper` и вызывает `bot.loop_wrapper.run()`.

Атрибут поллинга доступен как `bot.polling`.

---

# Минимальный рабочий пример бота на LongPoll

> Источник: <https://vkbottle.readthedocs.io/ru/latest/tutorial/first-bot/>

```python
from vkbottle.bot import Bot, Message

bot = Bot(token="token")


@bot.on.message(text="Привет")
async def hi_handler(message: Message):
    users_info = await bot.api.users.get(message.from_id)
    await message.answer("Привет, {}".format(users_info[0].first_name))


bot.run_forever()
```

## Обязательные настройки в настройках сообщества

Из туториала (первый бот):

> Если представленный код не работает, проверьте поставили ли вы галочки в настройках лонгпола на нужные события (в данном случае на новые сообщения) и сам лонгпол (**стабильна версия `5.131`**).

Из раздела про Callback (актуально и для понимания настроек):

> После подключения бот будет обрабатывать входящие сообщения, **для получения остальных событий необходимо включить их в настройках группы**.

---

# Мультибот: несколько лонгполов одновременно

> Источник: <https://vkbottle.readthedocs.io/ru/latest/high-level/bot/multibot/>

Мультибот запускает **несколько лонгполов** на переданных вами API и обрабатывает получаемые ивенты со всех лонгполов с помощью одного основного бота. Эта идея встречается например в чат-менеджере с их субменеджерами и может быть использована в разных целях.

## Запуск

Для запуска такого бота вам понадобится `run_multibot`, он добавляет `run_polling` в таски и запускает `eventloop`. Его можно импортировать из `vkbottle.bot`:

```python
run_multibot(bot, apis, polling_type=BotPolling)
```

- Основному боту **передавать токен для создания API не нужно**
- `apis` — любой итерируемый объект (то есть можно легко сделать свой генератор при желании)
- `polling_type` — если вы кастомизируете поллинг вы можете изменить это значение

Пример мультибота: <https://github.com/vkbottle/vkbottle/tree/master/examples/high-level/multibot.py>

---

# LongPoll vs Callback API

| | LongPoll | Callback API |
|---|---|---|
| Что нужно | ничего, кроме токена группы | собственный сервер с доменным именем (DDNS не работает) |
| Запуск | `bot.run_forever()` / `await bot.run_polling()` | `bot.setup_webhook()` + `await bot.process_event(event)` |
| Компонент | `bot.polling` (`BotPolling`) | `bot.callback` (`BotCallback`) |
| Где настраивать | галочки в настройках лонгпола сообщества | галочки в настройках события сообщества |
| Документация | этот файл | [10-callback.md](./10-callback.md) |

> Для большого проекта без своего сервера используем **LongPoll**.

---

# Связанные страницы

- [11-api.md](./11-api.md) — лимиты запросов и генераторы токенов (важно при работе с API)
- [13-faq.md](./13-faq.md) — почему только асинхронные библиотеки
- [03-handlers.md](./03-handlers.md) — `Bot`: атрибуты и функции

---

Далее: [10. Callback API](./10-callback.md)
