# web_service

Веб-сервис на базе Flask для Python 3.7

## Установка

```
git clone https://github.com/sedrew/web_service.git
cd web_service
pip install -r requirements.txt
```

создание базы данных
```
python
from app import db
db.create_all()
exit()
```
Создание популяции в БД

`python create_population.py`


## Запуск 

`python app.py`

## API

### User Api

##### GET - api/users

возвращает структуру из 2 полей

`total_count` - общее количество элементов с учетом фильтра

 `items` - список элементов с учетом пагинации
 
передаваемые параметры
1. offset - количество пропускаемых элементов (для пагинации)
2. limit - количество возвращаемых элементов (для пагинации)
3. order_by - сортировка по полю (name, last_name, email)
4. id - получение элемента по идентификатору
5. email - фильтр по полю email (совпадение по полной строке)
6. name_substr - фильтр по полю name (совпадение по подстроке)

Можно передать разное количество параметров

##### POST - api/users

возвращает структуру из 2 полей

`message` - сообщение о создание нового пользователя

`user` - список созданных параметров 

передаваемые параметры
1. name - имя
2. last_name - Фамилия
3. role - author или editor
4. state - один из параметров: active, inactive, deleted
5. email - электроная почта

Все передоваемые параметры проходят валидацию на тип, правильность указанного значения, пустые поля не принимаются.

### Post Api

##### GET - api/posts

возвращает структуру из 2 полей

`total_count` - общее количество элементов с учетом фильтра

 `items` - список элементов с учетом пагинации
 
передаваемые параметры
1. offset - количество пропускаемых элементов (для пагинации)
2. limit - количество возвращаемых элементов (для пагинации)
3. order_by - сортировка по полю (name, last_name, email)
4. author - фильтр по полю author

Можно передать разное количество параметров

##### POST - api/posts
возвращает структуру из 2 полей

`message` - сообщение о создание нового пользователя

`post` - список созданных параметров 

передаваемые параметры
1. title - загаловок
2. description - описание
3. author - id автора

Все передоваемые параметры проходят валидацию на тип, правильность указанного значения, пустые поля не принимаются.

## Example

#### Через консоль

```
python
import requests
```

GET - /api/users  

`requests.get('http://localhost:5000/api/users?limit=2&name_substr=&order_by=-name').json()`

Ответ
```json
{
    "items": [
        {
            "email": "28a@7m5a5il.r66u",
            "id": 19,
            "last_name": "s",
            "name": "sfs",
            "role": "author",
            "state": "active"
        },
        {
            "email": "28a@7m45a5il.r66u",
            "id": 20,
            "last_name": "s",
            "name": "sfs",
            "role": "author",
            "state": "active"
        }
    ],
    "total_count": [
        {
            "email": "28a@7m5a5il.r66u",
            "id": 19,
            "last_name": "s",
            "name": "sfs",
            "role": "author",
            "state": "active"
        },

 ```

POST - /api/posts

`requests.post('http://localhost:5000/api/posts', json=  {"title": "Космос","description": "Млечный путь","author": 1}).json()`

Ответ 
```json
{
    "message": "Created new post.",
    "post": {
        "author": 1,
        "description": "Млечный путь",
        "id": 67,
        "title": "Космос"
    }
}
```
#### Через Postman

POST - /api/users

###### Только для post запроса

В Headers выставить параметры `KEY` - `Content-Type`, `VALUE` - `application/json`

В Body выбрать raw в формате JSON

Составить запрос

```json
{
    "name": "Boris",
    "last_name": "Ivanov",
    "role": "author",
    "state": "active",
    "email": "28a-Dark@mail.ru"
}
```

Ответ 

```json
{
    "message": "Created new user.",
    "user": {
        "email": "28a-Dark@mail.ru",
        "id": 22,
        "last_name": "Ivanov",
        "name": "Boris",
        "role": "author",
        "state": "active"
    }
}
```
