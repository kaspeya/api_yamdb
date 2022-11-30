# YaMDb(docker-compose)


## Описание: 

Реализация API сервиса проекта YaMDb для обмена данными на базе DRF. Проект YaMDb cобирает отзывы (Review) пользователей на произведения (Titles). Произведения делятся на категории (Category): «Книги», «Фильмы», «Музыка». Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку. 
Произведению может быть присвоен жанр (Genre) из списка предустановленных (например, «Сказка», «Рок» или «Артхаус»). Новые жанры может создавать только администратор. Пользовательские оценки формируют рейтинг. На одно произведение пользователь может оставить только один отзыв. 

## Как запустить проект: 

### Шаблон наполнения env-файла ( расположение файла - infra/.env ):
``` 
SECRET_KEY=default-key
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=login
POSTGRES_PASSWORD=password
DB_HOST=db
DB_PORT=5432
```

### Установка
Для запуска приложения проделайте следующие шаги:


Склонируйте репозиторий:
``` 
git clone 
``` 
Перейдити в папку infra, создайте файл .env, заполните его данными из шаблона выше и запустите docker-compose.yaml (при установленном и запущенном Docker):
``` 
docker-compose up
``` 
Для пересборки контейнеров выполните команду:
``` 
docker-compose up -d --build
``` 
В контейнере web выполните миграции:
``` 
docker-compose exec web python manage.py migrate
``` 
Создатйте суперпользователя:
``` 
docker-compose exec web python manage.py createsuperuser
``` 
Соберите статику:
``` 
docker-compose exec web python manage.py collectstatic --no-input
``` 
Проект запущен и доступен по адресу: localhost


### Загрузка тестовых значений в БД:


Чтобы загрузить тестовые значения в базу данных перейдите в каталог проекта и скопируйте файл базы данных в контейнер приложения:
``` 
docker cp <DATA BASE> <CONTAINER ID>:/app/<DATA BASE>
``` 
Перейдите в контейнер приложения и загрузить данные в БД:
``` 

docker container exec -it <CONTAINER ID> bash
```
```
python manage.py loaddata <DATA BASE> 
``` 

При необходимости возможно импортировать тестовые данные:
```
docker-compose exec web python manage.py loaddata fixtures.json
