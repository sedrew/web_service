# web_service

Веб-сервис на базе Flask для Python 3

## Установка

`pip install -r requirements.txt`

создание базы данных
```
python
from app import db
db.create_all()
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
2. limit - количество возвращаемых элементов (для пагинации).
3. order_by - сортировка по полю (name, last_name, email).
4. id - получение элемента по идентификатору.
5. email - фильтр по полю email (совпадение по полной строке).
6. name_substr - фильтр по полю name (совпадение по подстроке).

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

Все передоваемые параметры проходят валидацию на тип, правлильность указанного значения, пустые поля не принимаются.

### Post Api

##### GET - api/posts

возвращает структуру из 2 полей

`total_count` - общее количество элементов с учетом фильтра

 `items` - список элементов с учетом пагинации
 
передаваемые параметры
1. offset - количество пропускаемых элементов (для пагинации)
2. limit - количество возвращаемых элементов (для пагинации).
3. order_by - сортировка по полю (name, last_name, email).
4. author - фильтр по полю author.

##### POST - api/posts
возвращает структуру из 2 полей

`message` - сообщение о создание нового пользователя

`post` - список созданных параметров 

передаваемые параметры
1. title - загаловок
2. description - описание
3. author - id автора

Все передоваемые параметры проходят валидацию на тип, правлильность указанного значения, пустые поля не принимаются.
