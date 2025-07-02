import os
from io import BytesIO

import aiohttp
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile, status
from PIL import Image

from deepai_service import DeepAIService
from models import ModerationResponse, ModerationStatus

# Загружаем переменные окружения
load_dotenv()

# Конфигурация
DEEPAI_API_KEY = os.getenv("DEEPAI_API_KEY", "")
NSFW_THRESHOLD = float(os.getenv("NSFW_THRESHOLD", "0.7"))
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

# Проверяем наличие API ключа
if not DEEPAI_API_KEY:
    raise ValueError("DEEPAI_API_KEY is required")

# Инициализируем сервис
deepai_service = DeepAIService(DEEPAI_API_KEY)

# Создание FastAPI приложения
app = FastAPI(
    title="NSFW Content Detector",
    description="API для модерации изображений",
    version="1.0.0",
)


@app.get("/health")
async def health_check():
    """Проверка состояния сервиса"""
    return {"status": "healthy"}


@app.post("/moderate", response_model=ModerationResponse)
async def moderate_image(file: UploadFile = File(...)):
    """
    Эндпоинт для модерации изображений
    """
    # Валидация файла
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    file_extension = file.filename.lower().split(".")[-1]
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unsupported file format. "
                f"Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            ),
        )

    try:
        # Чтение и валидация изображения
        image_data = await file.read()

        if len(image_data) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum: {MAX_FILE_SIZE} bytes",
            )

        # Проверяем что это валидное изображение
        with Image.open(BytesIO(image_data)) as img:
            img.verify()

        # Отправка в DeepAI API
        deepai_response = await deepai_service.detect_nsfw(
            image_data, file.filename
        )

        # Определение статуса модерации
        if deepai_response.nsfw_score > NSFW_THRESHOLD:
            return ModerationResponse(
                status=ModerationStatus.REJECTED, reason="NSFW content"
            )
        else:
            return ModerationResponse(status=ModerationStatus.OK)

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=str(e),
        )
    except aiohttp.ClientError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="External service unavailable",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
