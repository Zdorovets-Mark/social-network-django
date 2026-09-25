# Социальная сеть на Django + DRF

Учебный backend-проект социальной сети на Django + Django REST Framework.
Реализованы регистрация и авторизация по токену, публикации, комментарии,
лайки, загрузка изображений, простая HTML-страница приветствия и админ-панель.

> Проект выполнен в учебных целях. Основной фокус — серверная часть (REST API),
> поэтому фронтенд представлен минимальными HTML-страницами.

---

## Возможности

- Регистрация и авторизация пользователей
- Выдача токена при регистрации и входе
- CRUD для публикаций
- Уровни доступа к публикациям: `public`, `friends`, `private`
- CRUD для комментариев (вложены в публикацию)
- Лайки с режимом toggle: повторный запрос убирает лайк
- Загрузка изображений к публикации
- Валидация загружаемых файлов: размер до 5 МБ, форматы `jpg/jpeg/png/gif`
- Права доступа: владелец может редактировать/удалять, остальные — только читать
- Автоматическое удаление файла изображения при удалении записи `Photo`
- Админ-панель Django
- HTML-страницы: приветствие, вход, регистрация

---

## Стек технологий

- **Python** 3.10+
- **Django** 5.2.3
- **Django REST Framework** 3.16.0
- **TokenAuthentication** (`rest_framework.authtoken`)
- **PostgreSQL**
- **Pillow** — для `ImageField`
- **django-filter** — фильтрация
- **flake8 / isort / black** — качество кода

---

## HTML-страницы

| URL | Назначение |
|-----|------------|
| `/` | Приветственная страница |
| `/login/` | Страница входа |
| `/register/` | Страница регистрации |
| `/admin/` | Админ-панель Django |

---

## API

Базовый URL: `http://127.0.0.1:8000/`

Для защищённых запросов передавай заголовок:

```
Authorization: Token <твой_токен>
```

### Аутентификация

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/api/auth/register/` | Регистрация пользователя |
| POST | `/api/auth/login/` | Вход пользователя |

**Регистрация**

```http
POST /api/auth/register/
Content-Type: application/json

{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123"
}
```

**Вход**

```http
POST /api/auth/login/
Content-Type: application/json

{
    "username": "john_doe",
    "password": "SecurePass123"
}
```

В ответ приходит токен, `user_id`, `username` и сообщение.

---

### Публикации

| Метод | URL | Доступ | Описание |
|-------|-----|--------|----------|
| GET | `/api/publications/` | Все | Список публикаций |
| POST | `/api/publications/` | Аутентифицированные | Создать публикацию |
| GET | `/api/publications/{id}/` | Все | Детали публикации |
| PUT/PATCH | `/api/publications/{id}/` | Владелец | Обновить публикацию |
| DELETE | `/api/publications/{id}/` | Владелец | Удалить публикацию |
| POST | `/api/publications/{id}/like/` | Аутентифицированные | Поставить/убрать лайк |

**Создание публикации**

Запрос `multipart/form-data`, так как передаются файлы:

- `text` — текст публикации
- `photos` — одно или несколько изображений (от 1 до 10)

```http
POST /api/publications/
Authorization: Token <токен>
Content-Type: multipart/form-data
```

**Лайк**

```http
POST /api/publications/8/like/
Authorization: Token <токен>
```

Если лайка не было — он создаётся. Если уже был — удаляется.

---

### Комментарии

Комментарии вложены в публикацию.

| Метод | URL | Доступ | Описание |
|-------|-----|--------|----------|
| GET | `/api/publications/{publication_pk}/comments/` | Все | Список комментариев |
| POST | `/api/publications/{publication_pk}/comments/` | Аутентифицированные | Создать комментарий |
| GET | `/api/publications/{publication_pk}/comments/{id}/` | Все | Детали комментария |
| PUT/PATCH | `/api/publications/{publication_pk}/comments/{id}/` | Автор | Обновить комментарий |
| DELETE | `/api/publications/{publication_pk}/comments/{id}/` | Автор | Удалить комментарий |

**Создание комментария**

```http
POST /api/publications/8/comments/
Content-Type: application/json
Authorization: Token <токен>

{
    "text": "Первый комментарий"
}
```

**Обновление комментария**

```http
PUT /api/publications/8/comments/1/
Content-Type: application/json
Authorization: Token <токен>

{
    "text": "Обновлённый текст"
}
```

---

## Примеры запросов

Готовый набор запросов лежит в файле:

```
requests.http
```

Его можно открыть в PyCharm / IntelliJ IDEA / VS Code с плагином REST Client
и выполнять запросы прямо из редактора.

---

## Структура проекта

```
Diplom/
├── backend/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py          # Publication, Comment, Like, Photo
│   ├── permissions.py     # IsOwnerOrReadOnly
│   ├── serializers.py     # Сериализаторы DRF
│   ├── views.py           # APIView, ViewSet, HTML views
│   └── urls.py
├── my_diplom/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── templates/
│   ├── greeting.html
│   ├── login.html
│   └── register.html
├── media/                 # Загруженные файлы (создаётся автоматически)
├── manage.py
├── requirements.txt
├── requests.http
└── README.md
```

---

## Модели

### Publication

- `id_user` — автор публикации
- `text` — текст
- `accessibility` — уровень доступа (`public`, `friends`, `private`)
- `time_created` — дата создания

### Comment

- `id_user` — автор комментария
- `id_publication` — публикация
- `text` — текст
- `time_created` — дата создания

### Like

- `id_user` — пользователь
- `id_publication` — публикация
- `time_created` — дата создания
- Ограничение: один пользователь — один лайк на публикацию

### Photo

- `id_user` — пользователь, загрузивший фото
- `id_publication` — публикация (может быть пустой)
- `image` — изображение
- `caption` — подпись
- `time_created` — дата создания

---

## Качество кода

В проекте используются:

- `flake8` — проверка стиля
- `isort` — сортировка импортов
- `black` — автоформатирование

Примеры команд:

```bash
flake8 .
isort .
black .
```

---

## Примечания

- `MEDIA_ROOT` создаётся автоматически при старте приложения через `BackendConfig.ready()`.
- При удалении объекта `Photo` файл изображения удаляется с диска через сигнал `post_delete`.
- Для продакшена рекомендуется:
  - вынести `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, доступы к БД в переменные окружения;
  - использовать `gunicorn`/`uWSGI`;
  - раздавать `media` и `static` через nginx;
  - включить HTTPS.

---

## Планы развития

- Покрыть API тестами (`pytest-django`).
- Добавить JWT-аутентификацию (`djangorestframework-simplejwt`).
- Контейнеризовать проект (Docker + Docker Compose).
- Добавить пагинацию, кэширование и фильтрацию публикаций.
- Настроить CI (GitHub Actions) для запуска линтеров и тестов.

## Автор

Mark Zdorovets

GitHub: [@Zdorovets-Mark](https://github.com/Zdorovets-Mark)

---

## Лицензия

MIT License. Проект создан в учебных целях.
