# MAV-tg-crm 🤖

#### Используемый стек:


🐍 Python3.12
🐍 FastAPI 
🐍 SQLAlchemy2  
🐍 Dishka
🐍 Adaptix
🏷️ Postgres

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


Для интеграции direnv с оболочкой bash необходимо добавить соответствующий хук. Подробная инструкция доступна ниже

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

- Запуск без транслирования логов в консоль

```bash
make compose
```

- Запуск с логами в консоли (необходим Docker >= 2.22.0)

```bash 
make watch
```
- Запуск проекта без билда

```bash 
make untouch
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

Запуск линтеров по всему проекту:

```bash
make lint
```
