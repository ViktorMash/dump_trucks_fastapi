from pydantic import BaseModel, Field, ConfigDict


class TruckModelCreateSchema(BaseModel):
    """ Схема для создания/изменения модели самосвала """

    name: str = Field(
        default=...,
        max_length=50,
        description="Название модели"
    )
    max_capacity: int = Field(
        default=...,
        ge=1,
        description="Максимальная грузоподъемность (тонн)"
    )

    model_config = ConfigDict(
        from_attributes=True
    )


class TruckModelSchema(TruckModelCreateSchema):
    """Схема модели самосвала с ID"""

    id: int = Field(
        default=...,
        ge=1,
        description="Уникальный ID модели"
    )
