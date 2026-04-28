# Auth & RBAC Service

Backend-приложение с собственной системой аутентификации и авторизации на основе ролей (RBAC).

---

## Стек технологий

- **FastAPI** — веб-фреймворк
- **PostgreSQL** — база данных
- **SQLAlchemy** — ORM
- **Alembic** — миграции
- **JWT (python-jose)** — токены доступа
- **Passlib + bcrypt** — хэширование паролей

---

## Запуск проекта

```bash
# 1. Установить зависимости
pip install -r requirements.txt

# 2. Создать .env файл
cp .env.example .env
# Заполнить переменные окружения в .env

# 3. Применить миграции
alembic upgrade head

# 4. Заполнить тестовыми данными
python -m app.db.seed

# 5. Запустить сервер
uvicorn app.main:app --reload
```

Документация доступна по адресу: http://localhost:8000/docs

---

## Схема базы данных

### Таблица `users`
| Поле             | Тип          | Описание                        |
|------------------|--------------|---------------------------------|
| id               | INTEGER PK   | Первичный ключ                  |
| first_name       | VARCHAR(100) | Имя                             |
| last_name        | VARCHAR(100) | Фамилия                         |
| patronymic       | VARCHAR(100) | Отчество (опционально)          |
| email            | VARCHAR(255) | Email (уникальный)              |
| hashed_password  | VARCHAR(255) | Хэш пароля (bcrypt)             |
| is_active        | BOOLEAN      | Активен ли аккаунт              |
| created_at       | TIMESTAMP    | Дата создания                   |
| updated_at       | TIMESTAMP    | Дата последнего обновления      |

### Таблица `roles`
| Поле        | Тип         | Описание           |
|-------------|-------------|--------------------|
| id          | INTEGER PK  | Первичный ключ     |
| name        | VARCHAR(50) | Название роли      |
| description | TEXT        | Описание           |

### Таблица `permissions`
| Поле        | Тип         | Описание                        |
|-------------|-------------|---------------------------------|
| id          | INTEGER PK  | Первичный ключ                  |
| name        | VARCHAR(50) | Название (read, write, delete)  |
| description | TEXT        | Описание                        |

### Таблица `resources`
| Поле        | Тип          | Описание           |
|-------------|--------------|--------------------|
| id          | INTEGER PK   | Первичный ключ     |
| name        | VARCHAR(100) | Название ресурса   |
| description | TEXT         | Описание           |

### Связующие таблицы
- **`user_roles`** — связь пользователей и ролей (many-to-many)
- **`role_permissions`** — связь ролей и разрешений (many-to-many)
- **`role_resources`** — связь ролей и ресурсов (many-to-many)

---

## Модель разграничения прав доступа (RBAC)

Система использует **Role-Based Access Control (RBAC)**.

### Роли и их права

| Роль        | Разрешения              | Доступные ресурсы                    |
|-------------|-------------------------|--------------------------------------|
| `user`      | read                    | documents                            |
| `moderator` | read, write             | documents, reports                   |
| `admin`     | read, write, delete     | documents, reports, admin_panel      |

### Правила доступа

1. Каждый пользователь имеет одну или несколько ролей.
2. Каждая роль имеет набор разрешений (`read`, `write`, `delete`).
3. Каждая роль имеет доступ к определённым ресурсам.
4. При запросе к ресурсу система проверяет:
   - Аутентифицирован ли пользователь → иначе **401 Unauthorized**
   - Есть ли у пользователя доступ к данному ресурсу → иначе **403 Forbidden**
   - Есть ли у пользователя необходимое разрешение → иначе **403 Forbidden**

---

## API эндпоинты

### Аутентификация (`/auth`)

| Метод  | Путь          | Описание                              | Auth |
|--------|---------------|---------------------------------------|------|
| POST   | /auth/register | Регистрация нового пользователя       | ❌    |
| POST   | /auth/login    | Вход, получение JWT токена            | ❌    |
| POST   | /auth/logout   | Выход из системы                      | ✅    |
| GET    | /auth/me       | Получить профиль текущего пользователя| ✅    |
| PATCH  | /auth/me       | Обновить профиль                      | ✅    |
| DELETE | /auth/me       | Мягкое удаление аккаунта              | ✅    |

### Ресурсы (`/resources`)

| Метод  | Путь                      | Описание                    | Роли               |
|--------|---------------------------|-----------------------------|--------------------|
| GET    | /resources/               | Мои доступные ресурсы       | все                |
| GET    | /resources/my-permissions | Мои роли и разрешения       | все                |
| GET    | /resources/documents      | Просмотр документов         | user, moderator, admin |
| POST   | /resources/documents      | Создать документ (write)    | moderator, admin   |
| DELETE | /resources/documents/{id} | Удалить документ (delete)   | admin              |
| GET    | /resources/reports        | Просмотр отчётов            | moderator, admin   |
| GET    | /resources/admin_panel    | Панель администратора       | admin              |

---

## Тестовые аккаунты

После запуска `python -m app.db.seed`:

| Email                    | Пароль       | Роль       |
|--------------------------|--------------|------------|
| admin@example.com        | Admin1234!   | admin      |
| moderator@example.com    | Moder1234!   | moderator  |
| user@example.com         | User1234!    | user       |

---

## Мягкое удаление пользователя

При удалении аккаунта (`DELETE /auth/me`):
- Поле `is_active` устанавливается в `False`
- Запись в БД сохраняется
- Пользователь автоматически разлогинивается (JWT становится недействительным при следующей проверке)
- Попытка входа возвращает ошибку `401 Unauthorized`
