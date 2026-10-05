# 07. Стейты: State Dispenser и Waiter Machine

> Источники:
> - <https://vkbottle.readthedocs.io/ru/latest/high-level/handling/state-dispenser/>
> - <https://vkbottle.readthedocs.io/ru/latest/tools/waiter-machine/>

---

# State-Dispenser

StateDispenser'ы нужны, чтобы организовывать веточную систему организации пользователя. Сложное меню — стейты, квиз — стейты, какая-то игра — стейты.

## Методы StateDispenser

| Метод | Описание |
|---|---|
| `get(peer_id)` | Возвращает `StatePeer` (если запись на запрошенный peer_id существует) или `None` (если нет) |
| `set(peer_id, state)` | Делает запись |
| `delete(peer_id)` | Удаляет запись |

## Работа со стейтами

Получить стейт можно из объекта любого ивента: `event.state_peer.state`.

Чтобы задать стейт пользователю, достаточно воспользоваться методом `set`. Ловить пользователей со стейтами в хендлерами можно с помощью `StateRule`.

Пример:

```python
from vkbottle import BaseStateGroup
from vkbottle.bot import Message, Bot

bot = Bot("t")


class SuperStates(BaseStateGroup):
    AWKWARD_STATE = "awkward"
    CONFIDENT_STATE = "confident"
    TERRIFYING_STATE = "terrifying"


@bot.on.message(state=SuperStates.AWKWARD_STATE)  # StateRule(SuperStates.AWKWARD_STATE)
async def awkward_handler(message: Message):
    await message.answer("oi awkward")


@bot.on.message(lev="/die")
async def die_handler(message: Message):
    await bot.state_dispenser.set(message.peer_id, SuperStates.AWKWARD_STATE)
    return "ok"


bot.run_forever()
```

> **Примечание.** `.set()` может принимать `**payload`, который позже доступен как словарь из `message.state_peer.payload`:

```python
# ... In handler:
await bot.state_dispenser.set(message.peer_id, SuperStates.TERRIFYING_STATE, something=1)
# ... With state:
print(message.state_peer.payload["something"])  # 1
```

---

# Waiter Machine

Waiter Machine для создания быстрых воронок без потери скоупа. Таким образом с его помощью можно реализовать быстрые стейты и написать простейшие воронки.

**В отличии от State Dispenser, состояния никуда не сериализуются**, поэтому Waiter Machine не следует использовать для сложных стейтов, где важна консистентность проведения например транзакции или они активны долгое время.

Простейший пример:

```python
from vkbottle.bot import Bot, Message
from vkbottle.tools import WaiterMachine

bot = Bot("...")
wm = WaiterMachine()


@bot.on.message(text="/wm")
async def greeting(message: Message):
    await message.answer("Как тебя зовут?")
    # Следующая строчка остановит выполнение хендлера,
    # и исполнение пойдет дальше только когда будет получено
    # сообщение соответствующее заданным правилам
    # (в данном случае просто от того же пользователя)
    m, _ = await wm.wait(bot.on.message_view, message)
    await message.answer(f"Привет, {m.text.capitalize()}! Будем знакомы.")


bot.run_forever()
```

Из `.wait` возвращается tuple с двумя элементами:

1. Объект события которое разрешило ожидание (в примере выше — `Message`)
2. Контекст который был сформирован в ходе обработки события

Поэтому его можно сразу раскрыть в две переменные.

В `.wait` можно так же передать правила, и `default_behaviour` как именованный аргумент:

```python
await message.answer("Напиши мне твой номер телефона")
m, ctx = await wm.wait(bot.on.message_view, message, RegexRule(PHONE_NUMBER_REGEX), default_behaviour="Неверный формат, напиши еще раз в правильном формате")
```

`default_behaviour` может принимать Callable, куда придет событие, либо любой другой объект который будет передан в return manager привязаный к активному view и обработан — в примере выше это строка, которая будет отправлена как сообщение, в соответствии с имплементацией в return manager для view сообщений ботов.

`expiration` принимает `timedelta` или `int` (в секундах) для того чтобы ограничить время ожидания, если ивент придет позже чем `start_ts + expiration`, то будет вызван drop и ивент будет обработан в обычном view.

Метод `.drop` используется чтобы сбросить ожидание ивента по идентификатору.

---

Далее: [08. Обработка ошибок](./08-errors.md)
