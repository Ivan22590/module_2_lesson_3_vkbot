# 02. Правила (rules)

> Источники:
> - <https://vkbottle.readthedocs.io/ru/latest/tutorial/rules/>
> - <https://vkbottle.readthedocs.io/ru/latest/high-level/builtin-rules/>
> - <https://vkbottle.readthedocs.io/ru/latest/high-level/handling/rules/>

Для того чтобы хендлер ловил только нужные сообщения/другие ивенты, нужны правила (rules, рулзы — устоявшаяся транслитерация в комьюнити вкботла), в вкботле существует множество рулзов прямо из коробки.

> **Внимание.** Все встроенные рулзы работают только с объектами `Message` и `MessageEvent` из `vkbottle.bot`, для обработки сырых евентов нужно писать свою реализацию.

## Способы использования правил

### 1. Импорт напрямую

Импортировать их из `vkbottle.dispatch.rules.base` и использовать, инициализируя прямо в декораторе или в любой другой части кода:

```python
from vkbottle.dispatch.rules.base import CommandRule


@bot.on.message(CommandRule("say", ["!", "/"], 1))
async def say_handler(message: Message, args: tuple[str]):
    await message.answer(f"<<{args[0]}>>")
```

### 2. Шорткаты (kwargs в декораторе)

```python
@bot.on.message(command=("say", 1))
async def say_handler(message: Message, args: tuple[str]):
    await message.answer(f"<<{args[0]}>>")
```

> **Примечание.** Некоторые правила принимают в качестве аргумента итерируемый объект. Например, `CommandRule` принимает два аргумента: `command` и `args_count`, но при использовании шортката можно передавать их в кортеже: `@bot.on.message(command=("help", 0))`

## Полный список шорткатов custom rules

| Шорткат | Класс правила |
|---|---|
| `from_chat` | `PeerRule` |
| `mention` | `MentionRule` |
| `command` | `CommandRule` |
| `from_user` | `FromUserRule` |
| `peer_ids` | `FromPeerRule` |
| `sticker` | `StickerRule` |
| `attachment` | `AttachmentTypeRule` |
| `levenshtein` и `lev` | `LevenshteinRule` |
| `length` | `MessageLengthRule` |
| `action` | `ChatActionRule` |
| `payload` | `PayloadRule` |
| `payload_contains` | `PayloadContainsRule` |
| `payload_map` | `PayloadMapRule` |
| `func` | `FuncRule` |
| `coroutine` и `coro` | `CoroutineRule` |
| `state` | `StateRule` |
| `state_group` | `StateGroupRule` |
| `regexp` и `regex` | `RegexRule` |
| `macro` | `MacroRule` |
| `text` | `VBMLRule` |
| `fuzzy` | `FuzzyTextRule` |

Логику рулзов можно посмотреть [здесь](https://github.com/vkbottle/vkbottle/blob/master/vkbottle/dispatch/rules/base.py).

---

# Встроенные правила (полный справочник)

> Источник: <https://vkbottle.readthedocs.io/ru/latest/high-level/builtin-rules/>

### `PeerRule`

```
PeerRule(from_chat: bool = True)
```

Нужно для ограничения источника сообщения, `PeerRule(from_chat=False)` например, будет указывать на то, что сообщение должно быть из личного диалога с ботом.

### `MentionRule`

```
MentionRule(mention_only: bool = False)
```

Используется для проверки на то, что бот был упомянут в сообщении. Параметр `mention_only` используется чтобы указать, что кроме упоминания в сообщении быть ничего не должно, в ином случае из сообщения удаляется упоминание чтобы другие правила могли обработать уже сам текст.

### `CommandRule`

```python
CommandRule(
    command_text,
    prefixes,
    args_count = 0,
    sep = " "
)
```

Используется для того чтобы реагировать на команды. Команда выглядит так:

```
{prefix}{command_text}{sep.join(args)}
```

В `command_text` можно передать несколько вариантов названия команды. В `prefixes` можно передать несколько возможных префиксов (например: '/', '!'). В `args_count` передается количество обязательных аргументов с `sep` в качестве разделителя.

### `VBMLRule`

```python
VBMLRule(
    pattern,
    patcher = None,
    flags = None
)
```

Используется в качестве парсера текстов сообщений. Разметка vbml исторически была сделана специально для фреймворка, чтобы легко писать паттерны с валидируемыми аргументами.

Пример:

```python
rule = VBMLRule("/cmd <eggs:int>")
rst = await rule.check(Message(text="/cmd 11", ...))
assert rst == {"eggs": 11}
```

Больше документации: <https://github.com/tesseradecade/vbml/blob/master/docs/index.md>

### `RegexRule`

```
RegexRule(regexp)
```

Используется для проверки на соответствие текста сообщения регулярному выражению.

### `StickerRule`

```
StickerRule(sticker_ids = None)
```

Используется для того чтобы отлавливать отправку стикеров в сообщении. Если `sticker_ids = None`, то проходить будет любое сообщение содержащее стикер.

### `FromPeerRule`

```
FromPeerRule(peer_ids)
```

Используется для отлова сообщений отправленных пользователем/группой с одним из указанных ID.

### `AttachmentTypeRule`

```
AttachementTypeRule(attachment_types)
```

Используется для отлова сообщений с указанным типом вложений (например: `photo`).

### `ForwardMessagesRule`

Используется для того, чтобы проверить, что сообщение содержит в себе вложенные сообщения.

### `ReplyMessageRule`

```
ReplyMessageRule(reply_message: bool = True)
```

### `GeoRule`

Используется для того чтобы отлавливать сообщения с геометкой.

### `LevenshteinRule`

> **Deprecation.** На данный момент обсуждается удаление этого правила из новых версий из-за его неоптимальности. Вместо этого рекомендуется использовать `FuzzyTextRule`.

```
LevenshteinRule(levenshtein_texts, max_distance: int = 1)
```

Используется для fuzzy string matching'а. Может принимать `max_distance` — максимальное отклонение от заданного текста.

### `FuzzyTextRule`

```
FuzzyTextRule(texts, min_ratio: float = 0.7)
```

Используется для fuzzy string matching'а. Настраивается через `min_ratio` — минимальная *похожесть* сообщения с переданным текстом (от 0 до 1).

### `MessageLengthRule`

```
MessageLengthRule(min_length: int)
```

Используется для ограничения минимальной длины текстового сообщения.

### `ChatActionRule`

```
ChatActionRule(chat_action_types)
```

Используется для отлова событий в беседах (например: `chat_invite_user`). [Документация ВК по chat actions](https://dev.vk.ru/reference/objects/message#action)

### `PayloadRule`

```
PayloadRule(payload)
```

Проверяет что у сообщения payload равен одному из данных.

### `PayloadContainsRule`

```
PayloadContainsRule(payload_part)
```

Проверяет что в payload сообщения содержит данную часть.

### `PayloadMapRule`

```
PayloadMapRule(payload_map)
```

Используется для создания ассоциаций необходимых значений и типов в payload сообщений.

Такой payload как:

```python
{"name": "boba", "data": {"action": "do", "number": 12}}
```

Выражается таким payload map:

```python
PayloadMapRule({"name": str, "data": {"action": str, "number": int}})
```

Вместо типа данных так же можно передать валидатор (`ABCValidator`), функцию (она будет вызвана со значением из полезной нагрузки сообщения) или literal-значения — например, если `"name"` в полезной нагрузке должен быть всегда `"boba"`.

Пример:

```python
PayloadMapRule(
    {
        "name": "boba",
        "data": {
            "action": lambda x: x in ("do", "undo"),
            "number": int,
        }
    }
)
```

### `FromUserRule`

```
FromUserRule(from_user: bool = True)
```

Используется для проверки что сообщение было отправлено пользователем, а не ботом. При `from_user = False`, работает в обратную сторону, проверяет что сообщение отправлено ботом.

### `FuncRule`

```
FuncRule(func)
```

Принимает функцию, которая будет вызвана с единственным аргументом — событием. Функция должна вернуть bool или dict с обновлением контекста.

### `CoroutineRule`

```
CoroutineRule(coro)
```

Ответ проверки правила получается из переданной корутины.

### `StateRule`

```
StateRule(state)
```

Нужно для стейт-машины, проверяет что источник ивента находится в переданном состоянии. Если переданное состояние = `None`, то правило проверяет чтобы источник не находился ни в каком состоянии.

### `StateGroupRule`

```
StateGroupRule(state_group)
```

Проверяет что пользователь находится в нужной коллекции состояний.

---

## Создание собственных правил

> Источник: <https://vkbottle.readthedocs.io/ru/latest/tutorial/rules/>

> **Примечание.** Правило — это класс соответствующий интерфейсу `ABCRule`, который должен реализовать лишь один асинхронный метод `check`, принимающий ивент и возвращающий `False` если проверка пройдена не была и `True` либо словарь с аргументами, которые будут распакованы в хендлер как непозиционные аргументы.

### Создание правил напрямую

```python
from typing import Union

from vkbottle.bot import Message
from vkbottle.dispatch.rules import ABCRule


class MyRule(ABCRule[Message]):
    async def check(self, event: Message) -> bool:
        return len(event.text) < 100
```

Использование первым способом:

```python
@bot.on.message(MyRule())
```

Вторым способом рулзом `MyRule` в текущем состоянии воспользоваться не получится, из-за отсутствия каких-либо параметров правила, предлагается его кастомизировать с помощью метода `__init__`:

```python
# Новый вид правила
class MyRule(ABCRule[Message]):
    def __init__(self, lt: int = 100):
        self.lt = lt

    async def check(self, event: Message) -> bool:
        return len(event.text) < self.lt
```

Теперь, если предварительно (до объявления хендлеров) зарегистрировать правило в локальный лейблер:

```python
bot.labeler.custom_rules["my_rule"] = MyRule
```

Его можно будет использовать и вторым способом:

```python
@bot.on.message(my_rule=50)
```

### Создание правил через правила-врапперы

> **Примечание.** Есть так называемые правила-врапперы, правила — которые исполняют какой-то код который получают как параметры.

К правилам-врапперам из коробки можно отнести: `func`, шорткат для `FuncRule`; `coro` или `coroutine`, шорткат для `CoroutineRule`.

`FuncRule` принимает в качестве аргумента функцию (которая может быть лямбдой). Созданное напрямую правило `MyRule` можно заменить вот так:

```python
@bot.on.message(func=lambda message: len(message.text) < 100)
```

## Распаковка словаря из правила в хендлер

> Источник: <https://vkbottle.readthedocs.io/ru/latest/high-level/handling/handler/>

Если правило вернуло словарь, то он будет распакован и передан в качестве аргументов в хендлер, если он принимает их:

```python
# Кастомное правило MyRule возвращает словарь `{"some_key": "some_value"}`
@bot.on.message(MyRule())
async def some_key_handler(message: Message, some_key: str):
    await message.answer(f"some_key={some_value}")

@bot.on.message(MyRule())
async def regular_handler(message: Message):
    await message.answer("Этот хендлер не принимает аргумент 'some_key', поэтому он и не был передан")

@bot.on.message(MyRule())
async def kwargs_handler(message: Message, **kwargs: Any):
    await message.answer(f"В хендлере переданы аргументы: {kwargs}")
    # В хендлере переданы аргументы: {"some_key": "some_value"}
```

## Экземплы по этой части туториала

- [labeler-setup](https://github.com/vkbottle/vkbottle/tree/master/examples/high-level/labeler_setup.py)
- [rules-shortcuts](https://github.com/vkbottle/vkbottle/tree/master/examples/high-level/rules_shortcuts.py)

---

Далее: [03. Хендлеры, View, Router](./03-handlers.md)
