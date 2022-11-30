# Документация к API проекта «YaMDb» (v1) 


## Описание: 

Реализация API сервиса проекта YaMDb для обмена данными на базе DRF. Проект YaMDb cобирает отзывы (Review) пользователей на произведения (Titles). Произведения делятся на категории (Category): «Книги», «Фильмы», «Музыка». Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку. 
Произведению может быть присвоен жанр (Genre) из списка предустановленных (например, «Сказка», «Рок» или «Артхаус»). Новые жанры может создавать только администратор. Пользовательские оценки формируют рейтинг. На одно произведение пользователь может оставить только один отзыв. 

 
### Как запустить проект: 

Клонировать репозиторий и перейти в корневую папку проекта: 
``` 
git clone 
``` 
``` 
cd api_yamdb 
``` 
Cоздать и активировать виртуальное окружение: 
``` 
python3 -m venv env 
``` 
``` 
source env/bin/activate 
``` 
Установить зависимости из файла requirements.txt: 
``` 
python3 -m pip install --upgrade pip 
``` 
``` 
pip install -r requirements.txt 
``` 
Выполнить миграции: 
``` 
python3 manage.py migrate 
``` 
Запустить проект: 
``` 
python3 manage.py runserver 
``` 
Загрузка тестовой базы: 
``` 
python manage.py filldatabase 
``` 


### Самостоятельная регистрация новых пользователей: 

Пользователь отправляет POST-запрос с параметрами email и username на эндпоинт /api/v1/auth/signup/. 
Сервис YaMDB отправляет письмо с кодом подтверждения (confirmation_code) на указанный адрес email.
Пользователь отправляет POST-запрос с параметрами username и confirmation_code на эндпоинт /api/v1/auth/token/,
в ответе на запрос ему приходит token (JWT-токен). 

 
### Некоторые примеры запросов к API: 

 
#### Документация в формате [ReDoc](http://127.0.0.1:8000/redoc/). 

 
#### Примеры запросов: 

| CRUD      | Эндпоинты | Что получаем |  
| --- | --- | --- | 
| 'POST'    | /api/v1/auth/signup/                    | Регистрация.                           | 
| 'POST'    | /api/v1/auth/token/                     | Получение токена.                      | 
| 'GET'     | /api/v1/users/me/                       | Получение данных своей учетной записи. | 
| 'PATCH'   | /api/v1/users/me/                       | Изменение данных своей учетной записи. | 
| 'GET'     | /api/v1/titles/{title_id}/reviews/      | Получение отзывов.                     | 
| 'POST'    | /api/v1/titles/{title_id}/reviews/      | Добавление отзывов.                    | 
| 'DELETE'  | /api/v1/titles/{title_id}/reviews/      | Удаление отзывов.                      |

