# NSFW Content Detector

Простой сервер для модерации изображений с использованием DeepAI NSFW API.

## Установка и запуск

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Создайте файл `.env`:
```bash
cp .env.example .env
```

3. Получите API ключ на [DeepAI](https://deepai.org/dashboard) и добавьте его в `.env`:
```
DEEPAI_API_KEY=your_api_key_here
```

4. Запустите сервер:
```bash
python main.py
```

Сервер будет доступен по адресу: http://localhost:8000

## API

### POST /moderate

Принимает изображение (JPG, PNG) и возвращает результат модерации.

**Пример запроса:**
```bash
curl -X POST -F "file=@example.jpg" http://localhost:8000/moderate
```

**Ответы:**

Безопасное изображение:
```json
{"status": "OK"}
```

NSFW контент:
```json
{"status": "REJECTED", "reason": "NSFW content"}
```

### GET /health

Проверка состояния сервиса:
```bash
curl http://localhost:8000/health
```

## Настройки

В файле `.env` можно настроить:
- `DEEPAI_API_KEY` - API ключ DeepAI (обязательно)
- `NSFW_THRESHOLD` - порог NSFW (по умолчанию 0.7)
- `MAX_FILE_SIZE` - максимальный размер файла в байтах (по умолчанию 10MB)

## Логика модерации

- Если `nsfw_score > 0.7` → статус "REJECTED"
- Иначе → статус "OK" 