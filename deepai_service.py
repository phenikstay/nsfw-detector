import aiohttp

from models import DeepAIResponse


class DeepAIService:
    """Сервис для работы с DeepAI NSFW API"""

    BASE_URL = "https://api.deepai.org/api/nsfw-detector"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {"Api-Key": api_key}

    async def detect_nsfw(
        self, image_data: bytes, filename: str
    ) -> DeepAIResponse:
        """
        Отправляет изображение в DeepAI NSFW API для анализа

        Args:
            image_data: Бинарные данные изображения
            filename: Имя файла

        Returns:
            DeepAIResponse: Ответ с NSFW score
        """
        data = aiohttp.FormData()
        data.add_field(
            "image", image_data, filename=filename, content_type="image/jpeg"
        )

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.BASE_URL,
                headers=self.headers,
                data=data,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    if (
                        response.status == 401
                        and "Out of API credits" in error_text
                    ):
                        raise ValueError(
                            "DeepAI API: Закончились бесплатные кредиты. "
                            "Пожалуйста, пополните баланс в "
                            "https://deepai.org/dashboard"
                        )

                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=(
                            f"DeepAI API returned {response.status}: "
                            f"{error_text}"
                        ),
                    )

                response_data = await response.json()
                return DeepAIResponse(nsfw_score=response_data["nsfw_score"])
