# Документация по дипломному проекту

## Установка зависимостей
````
Выполните команду:
    pip install -r requirements.txt
````

## Настройка БД
````
1. Создать свою БД
2. Зайти в settings.py
2. Найти раздел
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "Netology_Diplom_Backend",
        "USER": "postgres",
        "PASSWORD": "3113",
        "HOST": "localhost",
        "PORT": 5432,
    }
}
3. Поменять параметры на ваши
````

## Запуск миграций
````
1. Запускать команды находясь на одном уровне с manage.py, либо использовать абсолютный путь 
2. Создать миграции
    python manage.py makemigrations
3. Применить созданные миграции
    python manage.py migrate
````

## Создание супер пользователя
````
1. Запускать команды находясь на одном уровне с manage.py, либо использовать абсолютный путь
2. Выполнить:
    python manage.py createsuperuser
3. Заполнить все поля
4. Если все поля введены правильно, система выдаст сообщение «Superuser created successfully».
````

## Примеры API запросов
````
Их можно найти в файле "requests.http"
````