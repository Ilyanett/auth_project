# Auth Project

Проект реализует систему аутентификации и авторизации на Django + PostgreSQL + JWT.

---

## Технологии

- Python 3.10+
- Django
- PostgreSQL
- PyJWT — создание и проверка токенов
- bcrypt — хэширование паролей

---

## Установка и запуск
```bash
# Клонируй проект и перейди в папку
cd auth_project

# Активируй виртуальное окружение
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Установи зависимости
pip install django djangorestframework psycopg2-binary PyJWT bcrypt python-dotenv

# Создай базу данных в PostgreSQL
psql -U postgres
CREATE DATABASE auth_db;
\q

# Скопируй шаблон и заполни своими данными
cp .env.example .env

# Применить миграции
python manage.py migrate

# Запустить сервер
python manage.py runserver


```

---

## Схема базы данных
```
users                          roles
─────────────────────          ──────────────
id                             id
email (unique)                 name (admin/manager/user/guest)
password_hash (bcrypt)         
first_name                     
last_name                      
is_active (мягкое удаление)    
created_at                     

user_roles                     business_elements
──────────────────             ─────────────────
id                             id
user_id → users.id             name (users/orders/products)
role_id → roles.id             

access_roles_rules             blacklisted_tokens
──────────────────────────     ──────────────────
id                             id
role_id → roles.id             token
element_id → business_elements.id  blacklisted_at
read_permission (bool)
read_all_permission (bool)
create_permission (bool)
update_permission (bool)
update_all_permission (bool)
delete_permission (bool)
delete_all_permission (bool)
```

---

## Схема прав доступа

| Роль    | Объект   | Читать своё | Читать всё | Создавать | Редактировать | Удалять |
|---------|----------|-------------|------------|-----------|---------------|---------|
| admin   | users    | ✅          | ✅         | ✅        | ✅            | ✅      |
| admin   | orders   | ✅          | ✅         | ✅        | ✅            | ✅      |
| admin   | products | ✅          | ✅         | ✅        | ✅            | ✅      |
| manager | orders   | ✅          | ✅         | ✅        | ✅            | ❌      |
| manager | products | ✅          | ✅         | ✅        | ✅            | ❌      |
| user    | orders   | ✅          | ❌         | ✅        | ✅            | ❌      |
| user    | products | ✅          | ✅         | ❌        | ❌            | ❌      |
| guest   | products | ✅          | ✅         | ❌        | ❌            | ❌      |

---

## Как работает аутентификация
```
1. Пользователь отправляет email + пароль на POST /api/login/
2. Сервер проверяет пароль через bcrypt
3. Сервер создаёт JWT токен с user_id внутри (живёт 24 часа)
4. Пользователь сохраняет токен и отправляет его в каждом запросе:
   Authorization: Bearer <токен>
5. Middleware читает токен, проверяет подпись и кладёт
   пользователя в request.user_obj
6. При logout токен добавляется в blacklisted_tokens
   и больше не принимается
```

---

## API endpoints

### Аутентификация

| Метод | URL | Описание | Авторизация |
|-------|-----|----------|-------------|
| POST | /api/register/ | Регистрация | Нет |
| POST | /api/login/ | Вход, возвращает токен | Нет |
| POST | /api/logout/ | Выход | Да |
| GET | /api/profile/ | Просмотр профиля | Да |
| PATCH | /api/profile/ | Изменение профиля | Да |
| DELETE | /api/profile/delete/ | Удаление аккаунта | Да |

### Бизнес объекты

| Метод | URL | Описание | Минимальная роль |
|-------|-----|----------|-----------------|
| GET | /api/orders/ | Список заказов | user |
| POST | /api/orders/ | Создать заказ | user |
| GET | /api/products/ | Список продуктов | guest |
| POST | /api/products/ | Создать продукт | manager |

### Администратор

| Метод | URL | Описание | Роль |
|-------|-----|----------|------|
| GET | /api/admin/rules/ | Все правила доступа | admin |
| PATCH | /api/admin/rules/ | Изменить правило | admin |
| GET | /api/admin/users/ | Все пользователи | admin |

---

## Тестовые пользователи

| Email | Пароль | Роль |
|-------|--------|------|
| admin@mail.com | admin123 | admin |
| user@mail.com | user123 | user |

---

## Коды ответов

| Код | Meaning |
|-----|---------|
| 200 | Успешный запрос |
| 201 | Объект создан |
| 400 | Ошибка в данных запроса |
| 401 | Не авторизован |
| 403 | Нет доступа |
| 404 | Объект не найден |


