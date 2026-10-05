# 05. Клавиатуры, вложения, шаблоны, загрузчики

> Источники:
> - <https://vkbottle.readthedocs.io/ru/latest/tutorial/keyboards-attachments/>
> - <https://vkbottle.readthedocs.io/ru/latest/tools/keyboard/>
> - <https://vkbottle.readthedocs.io/ru/latest/tools/template/>
> - <https://vkbottle.readthedocs.io/ru/latest/tools/uploaders/>

---

# Клавиатура (Keyboard)

> Подразумевается, что вы уже ознакомились с [документацией вк](https://dev.vk.ru/api/bots/development/keyboard).

Импортируйте `Keyboard`, `KeyboardButtonColor` и нужные вам `action` (например: `Text`, `OpenLink`, `Location`, `VKApps`, `Callback`).

```python
from vkbottle import Keyboard, KeyboardButtonColor, Text

keyboard = Keyboard(one_time=True, inline=False)
# О параметрах one_time и inline вы можете прочитать в документации к апи вконтакте
keyboard.add(Text("Кнопка 1"), color=KeyboardButtonColor.POSITIVE)
# Первая строка (ряд) добавляется автоматически
keyboard.row()  # Переходим на следующую строку
keyboard.add(Text("Кнопка 2"))
keyboard.add(Text("Кнопка 3", payload={"command": 3}))
```

Чтобы получить `json` для отправки клавиатуры в сообщении, используйте метод объекта клавиатуры `get_json()`:

```python
await message.answer(message="Смотри сколько кнопок!!", keyboard=keyboard.get_json())
```

### Интерфейс билдера

Для клавиатуры доступен интерфейс билдера, поэтому весь код выше можно заменить этим:

```python
from vkbottle import Keyboard, KeyboardButtonColor, Text

# ...
keyboard = (
    Keyboard(one_time=True, inline=False)
    .add(Text("Кнопка 1"), color=KeyboardButtonColor.POSITIVE)
    .row()
    .add(Text("Кнопка 2"))
    .add(Text("Кнопка 3", payload={"command": 3}))
).get_json()
await message.answer(
    message="Смотри сколько кнопок!!",
    keyboard=keyboard)
```

> **Примечание.** Для того, чтобы удалить клавиатуру у пользователя, вам нужно отправить `EMPTY_KEYBOARD`.

### Методы `Keyboard`

- `add(action, color)` — добавляет кнопку к текущему ряду кнопок;
- `row()` — создаёт следующий ряд кнопок, переводит "курсор" на него;
- `get_json()` — преобразует клавиатуру в JSON-объект, который можно отправить в сообщении.

`Keyboard` принимает параметры `one_time` и `inline` (их значение описано [здесь](https://vk.ru/dev/bots_docs_3?f=4.2.%20Структура%20данных)).

Создание клавиатуры использует `json.dumps` для преобразования в JSON-объект. Если ваша клавиатура статична, то вы можете избежать этой повторяющейся операции, создав её один раз, и используя уже "преобразованную" клавиатуру.

Отправка:

```python
keyboard = ...  # see examples above


@bot.on.message()
async def send_keyboard(message):
    await message.answer("Here is your keyboard!", keyboard=keyboard)
```

---

# Вложения

### Если у вас уже есть ссылка на вложение

Если у вас уже есть ссылка на вложение вида `"type{OWNER_ID}_{ITEM_ID}"` (например `"photo-41629685_457239401"`), то вы можете отправить её так:

```python
attachment = ...  # see example above


@bot.on.message
async def send_attachment(message):
    await message.answer("See that attachment!", attachment=attachment)
```

### Если вы загружаете вложения динамически

Для того чтобы отправлять вложения, загруженные во время работы бота, нужны загрузчики (см. раздел [Uploaders](#загрузчики-uploaders)).

Пример отправки вложения, полученного из загрузчика:

```python
uploader = AnyUploader(bot.api)  # see uploaders types in "Uploaders documentation" above


@bot.on.message()
async def send_attachment(message):
    attachment = await uploader.upload("path/to/file")
    await message.answer("See that attachment!", attachment=attachment)
```

---

# Шаблоны (Template)

На данный момент ВКонтакте поддерживает только один вид шаблона — **карусель**. Документация по этому виду шаблона представлена [здесь](https://vk.ru/dev/bot_docs_templates?f=5.%20Шаблоны%20сообщений).

Вы можете создать шаблон через vkbottle с помощью:

- `TemplateElement` — элемент шаблона. Названия полей соответствуют названиям полей в документации ВКонтакте.
- `template_gen` — создаёт шаблон из предоставленных элементов.

```python
from vkbottle import TemplateElement, template_gen

my_template = template_gen(
    TemplateElement(...),  # о том как нужно сочетать параметры можно
    TemplateElement(...)   # прочитать в документации Вконтакте выше
)
# my_template - готовый для отправки json
# ...
await message.answer("Держи карусель!", template=my_template)
```

---

# Загрузчики (Uploaders)

Загрузка медиа разного типа в ВК. Существует несколько типов аплоадеров:

- `audio` — загрузка аудио
- `doc` — загрузка документов разного типа
- `photo` — загрузка фото
- `speech` — загрузка аудиофайлов для распознавание речи
- `video` — загрузка видео

## Пример

```python
from vkbottle import PhotoMessageUploader
from vkbottle.bot import Bot

bot = Bot("token")
photo_uploader = PhotoMessageUploader(bot.api)


@bot.on.message(text="photo")
async def handler(message):
    photo = await photo_uploader.upload(
        file_source="photo.png",
        peer_id=m.peer_id,
    )
    await message.answer(attachment=photo)


bot.run_forever()
```

## Интерфейс аплоадера

Аплоадер принимает объект `API` при инициализации. У аплоадера два метода:

- `.upload(...)`
- `.raw_upload(...)`

Оба метода имеют одинаковый интерфейс, но различаются в том, что первый метод возвращает готовую строку аттачмента, а второй — словарь с ответом сервера.

> **Внимание.** Не все аплоадеры имеют метод `upload`, для них невозможно вернуть строку аттачмента.

Все аплоадеры различаются методом получения сервера. Получить сервер аплоадера можно с помощью метода `.get_server(...)`.

Так же у аплоадеров есть методы базового класса, одинаковые для всех:

- `.upload_files(url, files)` — загрузка файлов методом POST
- `.get_bytes_io(data)` — приводит сырые байты в подходящий для вк вид
- `.generate_attachment_string(attachment_type, owner_id, item_id, access_key)` — делает строку, которую вк принимает, как медиа для отправки
- `.read(file_source)` — читает файл, если `file_source` строка, а если байты — возвращает их

Обычно нужен только метод `upload`.

## Виды аплоадеров

**Для фото:**
- `PhotoMessageUploader` — загрузка в сообщение
- `PhotoToAlbumUploader` — загрузка в альбом
- `PhotoWallUploader` — загрузка на стену
- `PhotoFaviconUploader` — загрузка аватарки
- `PhotoChatFaviconUploader` — загрузка аватарки беседы
- `PhotoMarketUploader` — загрузка картинки для товара

**Для документов:**
- `DocWallUploader` — загрузка документов на стену
- `DocMessagesUploader` — загрузка документов в сообщение
- `VoiceMessageUploader` — загрузка голосовых сообщений
- `GraffitiUploader` — загрузка граффити

**Прочее:**
- `AudioUploader` — загрузка аудио
- `VideoUploader` — загрузка видео

## Дополнительные примеры

- [Uploaders example](https://github.com/vkbottle/vkbottle/blob/master/examples/high-level/uploaders_example.py)
- [Создание клавиатуры](https://github.com/vkbottle/vkbottle/tree/master/examples/high-level/generate_keyboard.py)

---

Далее: [06. Мидлвари](./06-middleware.md)
