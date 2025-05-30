from typing import List, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.trucks import ModelTruck
from app.schemas.http_response import ModelNotFoundError, DuplicateModelNameError
from app.schemas import TruckModelCreateSchema


async def create_model(
        db: AsyncSession,
        payload: TruckModelCreateSchema
) -> ModelTruck:
    """Создать модель самосвала"""

    # Проверяем уникальность названия модели
    stmt = select(ModelTruck.id).where(
        ModelTruck.name.ilike(payload.name)
    )
    if await db.scalar(stmt):
        raise DuplicateModelNameError("Модель с таким названием уже существует")

    model = ModelTruck(**payload.model_dump())
    db.add(model)
    await db.commit()
    await db.refresh(model)
    return model


async def read_models(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        count_total: bool = False
) -> List[ModelTruck] | Tuple[List[ModelTruck], int]:
    """ Получить список всех моделей """

    # Подсчет общего количества (если нужен)
    total_count = None
    if count_total:
        count_stmt = select(func.count(ModelTruck.id))
        total_count = await db.scalar(count_stmt)

    stmt = (
        select(ModelTruck)
        .order_by(ModelTruck.name)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    models = list(result.scalars().all())

    if count_total:
        return models, total_count
    return models


async def read_model_by_id(
        db: AsyncSession,
        model_id: int
) -> ModelTruck:
    """ Получить модель по ID """

    model = await db.get(ModelTruck, model_id)
    if not model:
        raise ModelNotFoundError(f"Модель с ID {model_id} не найдена")
    return model


async def update_model(
        db: AsyncSession,
        model: ModelTruck,
        payload: TruckModelCreateSchema
) -> ModelTruck:
    """ Обновить модель самосвала """

    # Проверяем уникальность названия если оно меняется
    if payload.name.lower() != model.name.lower():
        stmt = select(ModelTruck.id).where(
            ModelTruck.name.ilike(payload.name),
            ModelTruck.id != model.id,
        )
        if await db.scalar(stmt):
            raise DuplicateModelNameError("Модель с таким названием уже существует")

    model.name = payload.name
    model.max_capacity = payload.max_capacity

    await db.commit()
    await db.refresh(model)
    return model


async def delete_model(
        db: AsyncSession,
        model: ModelTruck
) -> None:
    """Удалить модель самосвала"""

    await db.delete(model)
    await db.commit()