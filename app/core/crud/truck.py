from typing import List, Optional, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.trucks import DumpTruck, ModelTruck
from app.schemas import DumpTruckCreateSchema
from app.schemas.http_response import (
    TruckNotFoundError, TruckModelNotFoundError, DuplicateBoardNumberError
)


async def create_truck(
    db: AsyncSession,
    payload: DumpTruckCreateSchema
) -> DumpTruck:
    """ Создать самосвал """

    # валидация модели
    model = await db.get(ModelTruck, payload.model_id)
    if not model:
        raise TruckModelNotFoundError("Модель самосвала с таким ID не найдена")

    # уникальность бортового номера
    stmt = select(DumpTruck.id).where(
        DumpTruck.board_number.ilike(payload.board_number)
    )
    if await db.scalar(stmt):
        raise DuplicateBoardNumberError("Самосвал с таким бортовым номером уже существует")

    truck = DumpTruck(**payload.model_dump())
    db.add(truck)
    await db.commit()
    await db.refresh(truck)

    await db.refresh(truck, ['model'])
    return truck


async def get_truck_by_id(
    db: AsyncSession,
    truck_id: int
) -> DumpTruck:
    """ Получить самосвал по ID """
    stmt = select(DumpTruck).options(selectinload(DumpTruck.model)).where(DumpTruck.id == truck_id)
    result = await db.execute(stmt)
    truck = result.unique().scalar_one_or_none()
    if not truck:
        raise TruckNotFoundError(f"Самосвал с ID {truck_id} не найден")
    return truck


async def get_trucks_list(
    db: AsyncSession,
    board_number: Optional[str] = None,
    model_name: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[List[DumpTruck], int]:
    """
        Получить список самосвалов с фильтрацией и пагинацией.
        :return (список самосвалов, общее количество)
    """
    stmt = (
        select(DumpTruck)
        .options(selectinload(DumpTruck.model))
        .order_by(DumpTruck.id)
    )

    # Фильтры
    if board_number:
        stmt = stmt.where(
            DumpTruck.board_number.ilike(f"%{board_number}%")
        )

    if model_name:
        stmt = stmt.where(
            DumpTruck.model.has(ModelTruck.name.ilike(f"%{model_name}%"))
        )

    # Подсчет общего количества
    count_stmt = select(func.count(DumpTruck.id))

    if board_number:
        count_stmt = count_stmt.where(
            DumpTruck.board_number.ilike(f"%{board_number}%")
        )
    if model_name:
        count_stmt = count_stmt.where(
            DumpTruck.model.has(ModelTruck.name.ilike(f"%{model_name}%"))
        )

    total_count = await db.scalar(count_stmt)

    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    trucks = list(result.unique().scalars().all())

    return trucks, total_count


async def update_truck(
    db: AsyncSession,
    truck: DumpTruck,
    payload: DumpTruckCreateSchema,
) -> DumpTruck:
    """
        Обновление самосвала
        Если меняется id модели – проверяем существование модели.
        Если меняется board_number – проверяем уникальность.
    """

    # Проверяем изменение модели
    if payload.model_id != truck.model_id:
        if not await db.get(ModelTruck, payload.model_id):
            raise TruckModelNotFoundError("Новая модель самосвала не найдена")

    # Проверяем уникальность бортового номера
    if payload.board_number.lower() != truck.board_number.lower():
        stmt = select(DumpTruck.id).where(
            DumpTruck.board_number.ilike(payload.board_number),
            DumpTruck.id != truck.id,
        )
        if await db.scalar(stmt):
            raise DuplicateBoardNumberError("Самосвал с таким бортовым номером уже существует")

    truck.model_id = payload.model_id
    truck.board_number = payload.board_number
    truck.current_weight = payload.current_weight

    # Перезагружаем объект со всеми связями
    await db.refresh(truck)
    stmt = select(DumpTruck).options(selectinload(DumpTruck.model)).where(DumpTruck.id == truck.id)
    result = await db.execute(stmt)
    refreshed_truck = result.unique().scalar_one()

    return refreshed_truck


async def delete_truck(db: AsyncSession, truck: DumpTruck) -> None:
    """ Удалить самосвал """

    await db.delete(truck)
    await db.commit()