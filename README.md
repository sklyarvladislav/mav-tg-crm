# MAV-tg-crm 🤖

#### Используемый стек:


- 🐍 Python3.12
- 🐍 FastAPI
- 🐍 SQLAlchemy 2
- 🐍 Dishka
- 🐍 Adaptix
- 🐍 Alembic
- 🗃 PostgreSQL
- 🐳 Docker + docker-compose
- ⚙️ uv


---

# 📗 1. Установка

## Убедитесь, что direnv установлен. Если нет, установите его:

```bash
brew install direnv # Для macOS
sudo apt install direnv # Для Ubuntu/Debian
sudo pacman -S direnv # для Arch
```

## При первом запуске необходимо настроить переменные окружения:

```bash
direnv allow .
```

[Хуки для direnv](https://direnv.net/docs/hook.html)

## Скопируйте файл примера конфигурации в рабочий конфиг и актуализируйте его данными:

```bash
cp infra/example.config.toml infra/config.toml
```

## Инициализируйте виртуальное окружения и синхронизируйте зависимости

- Инициализация
```bash
uv venv
```

- Синхронизация зависимостей
```bash
uv sync
```
# 📗 2. Запуск проекта

## 2.1. Запуск проекта при помощи докера

- Запуск проекта
```bash
make compose
```

- Запуск с логами в консоли без билда (Docker version >2.22.0 и редактировать весь python код возможно без выхода из режима)
```bash
make watch
```

- Остановка сервисов
```bash
make down
```

# 📗 3. Работа с проектом

## 3.1. Процесс настройки проекта

- Активируем окружение;
```bash
uv venv
```

- Устанавливаем зависимости;
```bash
uv sync
```

- Ставим pre-commit для линта кода;
```bash
uv run pre-commit install
```

## 3.2 Линтеры

Запуск линтер по проекту:
```bash
make lint
```

## 3.2. Работа с базой данных

- Накатить существующие миграции после сборки проекта
```bash
make upgrade
```

- Отменить последнюю миграцию
```bash
make downgrade
```

- Создать миграцию
```bash
make migration MSG="{name_of_migration}"
```


created by MAV team 💙
