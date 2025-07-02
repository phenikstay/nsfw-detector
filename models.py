from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ModerationStatus(str, Enum):
    """Статус модерации"""

    OK = "OK"
    REJECTED = "REJECTED"


class ModerationResponse(BaseModel):
    """Ответ на запрос модерации"""

    status: ModerationStatus
    reason: Optional[str] = None


class DeepAIResponse(BaseModel):
    """Ответ от DeepAI API"""

    nsfw_score: float = Field(..., ge=0.0, le=1.0)
