# Avito Tests Project

Проект для тестирования API Avito.

## Установка и настройка

**Клонирование репозитория**
```bash
git clone <url-репозитория>
cd AVITO_QA
```
**Создание виртуального окружения**
```bash
python -m venv .venv
```
**Активация виртуального окружения**
Windows
```bash
.venv\Scripts\activate
```
Linux/Mac
```bash
source .venv/bin/activate
```

**Установка зависимостей**

```bash
pip install -r requirements.txt
```

**Настройка переменных окружения**
Создайте .env файл, по умолчанию 666321
```bash
USERID=ваш_user_id 
```

## Запуск тестов

```bash
pytest -v
``` 