from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, field_validator
from .truck_models import TruckModelSchema


class DumpTruckCreateSchema(BaseModel):
    """ Схема для создания/изменения самосвала """

    model_id: int = Field(
        default=...,
        ge=1,
        description="ID модели самосвала"
    )
    board_number: str = Field(
        default=...,
        max_length=10,
        description="Бортовой номер в верхнем регистре",
    )
    current_weight: Optional[int] = Field(
        default=0,
        ge=0,
        description="Текущий вес груза (тонн)",
    )
    model_config = ConfigDict(
        from_attributes=True
    )


class DumpTruckSchema(DumpTruckCreateSchema):
    """ Параметры конкретного самосвала """

    id: int = Field(
        default=...,
        ge=1,
        description="Уникальный ID модели"
    )
    model: TruckModelSchema = Field(
        default=...,
        description="Модель самосвала"
    )
    overload_percentage: float = Field(
        default=...,
        ge=0,
        description="Процент перегруза (сверх 100%)",
    )
    is_overloaded: bool = Field(
        default=...,
        description="Перегружен ли самосвал",
    )

    @field_validator('current_weight')
    @classmethod
    def validate_current_weight(cls, v):
        if v < 0:
            raise ValueError('Текущий вес не может быть отрицательным')
        if v > 500:
            raise ValueError('Текущий вес не может превышать 500 тонн')
        return v

    @field_validator('board_number')
    @classmethod
    def validate_board_number(cls, v):
        if not v or not v.strip():
            raise ValueError('Бортовой номер не может быть пустым')
        return v.strip().upper()

    model_config = ConfigDict(
        from_attributes=True
    )