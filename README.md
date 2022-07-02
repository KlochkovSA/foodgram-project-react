# Foodgram
![CI](https://github.com/klochkovsa/foodgram-project-react/actions/workflows/main.yaml/badge.svg)


## The description
The foodgram is the recipe exchange service.
- users can create recipes, save others' recipes to favorites and subscribe to authors
- The builtin service 'Список покупок' (_eng: 'Product list'_) allows users to download the list of ingredients
for chosen recipes

## Stack:
 - Python 3.10
 - Django 4.0
 - Django REST framework
 - Djoser
 - gunicorn
 - python-dotenv
 - Docker, docker-compose


## The local deployment
1. Copy the repo, create and fill .env file in the repository root using this pattern
```
    DJANGO_KEY='secretKEY+-*'
    DB_ENGINE='django.db.backends.postgresql'
    DB_NAME='postgres'
    POSTGRES_USER='postgres'
    POSTGRES_PASSWORD='postgres'
    DB_HOST='db'
    DB_PORT=5432
```
2. Build the docker containers, create superuser and enjoy
```sh
sudo docker build -f ../backend/foodgram/Dockerfile -t klochkovsa/foodgram:v1 ../backend/foodgram
sudo docker compose -f infra/docker-compose.yml up -d
sudo docker compose -f infra/docker-compose.yml exec web python manage.py collectstatic --noinput
sudo docker compose -f infra/docker-compose.yml exec web python manage.py migrate
sudo docker compose -f infra/docker-compose.yml exec web python manage.py create superuser
```

Notes:
An the moment the service is available at
[klochkovsa.sytes.net]((http://http://klochkovsa.sytes.net))

admin_login = root

admin_password = practicum

# Authors
### Frontend - @yandex-praktikum
### Backend - @klochkovsa