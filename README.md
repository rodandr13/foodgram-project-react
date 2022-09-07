# Foodgram — продуктовый помощник.

На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/rodandr13/foodgram-project-react.git

cd /foodgram-project-react/infra
```
Развернуть приложение:
```
docker-compose up -d --build
```
Выполнить миграции
```
docker-compose exec web python manage.py migrate
```
Заполнить базу данными
```
docker-compose exec web python manage.py loaddata fixtures.json
```
Загрузить статику
```
docker-compose exec web python manage.py collectstatic --no-input
```


## Используемые технологии
- Python 3.10
- Django 3.2.15
- Django REST framework 3.13.1
- PostgreSQL
- Nginx
- Docker
## Автор
Родителев Андрей