from typing import Optional

from fastapi import APIRouter, Depends, Path, Query, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.db.models import DumpTruck
from app.schemas import DumpTruckCreateSchema
from app.schemas.http_response import ResponseSchema, ErrorResponseSchema
from app.core.response_api import api_response
from app.core.crud import (
    create_truck, read_truck, update_truck, delete_truck
)
from app.core.crud.truck_model import read_models
from app.schemas.http_response import (
    TruckNotFoundError, TruckModelNotFoundError, DuplicateBoardNumberError
)

trucks_router = APIRouter(
    prefix="/trucks",
    tags=["dump-trucks"],
)


# ──── CREATE ────
@trucks_router.post(
    "/",
    response_model=ResponseSchema,
    responses={
        201: {"model": ResponseSchema},
        404: {"model": ErrorResponseSchema},
        409: {"model": ErrorResponseSchema},
    },
    summary="Добавить новый самосвал в БД",
    status_code=status.HTTP_201_CREATED,
)
async def add_truck(
    truck_in: DumpTruckCreateSchema,
    db: AsyncSession = Depends(get_db),
):
    try:
        truck = await create_truck(db, truck_in)
        return api_response.success(
            data=truck,
            status_code=status.HTTP_201_CREATED,
        )
    except TruckModelNotFoundError as e:
        return api_response.error(
            error="Модель не найдена",
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except DuplicateBoardNumberError as e:
        return api_response.error(
            error="Дубликат бортового номера",
            message=str(e),
            status_code=status.HTTP_409_CONFLICT,
        )

# ──── READ (список самосвалов) ────
@trucks_router.get(
    "/",
    response_model=ResponseSchema,
    summary="Получить список самосвалов в БД",
)
async def list_dump_trucks(
    request: Request,
    board_number: Optional[str] = Query(default=None, description="Фильтр по бортовому номеру"),
    model_name: Optional[str] = Query(default=None, description="Фильтр по модели"),
    page: int = Query(default=1, ge=1, description="Номер страницы"),
    per_page: int = Query(default=50, ge=1, le=100, description="Количество записей на странице"),
    db: AsyncSession = Depends(get_db),
):
    skip = (page - 1) * per_page

    trucks, total_count = await read_truck(
        db=db,
        truck_id=None,
        board_number=board_number,
        model_name=model_name,
        skip=skip,
        limit=per_page,
    )

    return api_response.success(
        data=trucks,
        total=total_count,
        page=page,
        per_page=per_page,
        request=request,
    )

# ──── READ (Модели самосвалов) ────
@trucks_router.get(
    "/models",
    response_model=ResponseSchema,
    summary="Получить список всех моделей самосвалов",
)
async def list_truck_models(
    request: Request,
    page: int = Query(default=1, ge=1, description="Номер страницы"),
    per_page: int = Query(default=100, ge=1, le=100, description="Количество записей на странице"),
    db: AsyncSession = Depends(get_db),
):
    skip = (page - 1) * per_page
    models, total_count = await read_models(
        db=db,
        skip=skip,
        limit=per_page,
        count_total=True
    )

    return api_response.success(
        data=models,
        total=total_count,
        page=page,
        per_page=per_page,
        request=request,
    )

# ──── READ (один самосвал) ────
@trucks_router.get(
    "/{truck_id}",
    response_model=ResponseSchema,
    responses={
        200: {"model": ResponseSchema},
        404: {"model": ErrorResponseSchema},
    },
    summary="Получить данные по ID самосвала",
)
async def get_dump_truck(
    truck_id: int = Path(default=..., ge=1),
    db: AsyncSession = Depends(get_db),
):
    try:
        truck = await read_truck(db=db, truck_id=truck_id)
        return api_response.success(data=truck)
    except TruckNotFoundError as e:
        return api_response.error(
            error="TruckNotFound",
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND,
        )


# ──── UPDATE ────
@trucks_router.put(
    "/{truck_id}",
    response_model=ResponseSchema,
    responses={
        200: {"model": ResponseSchema},
        404: {"model": ErrorResponseSchema},
        409: {"model": ErrorResponseSchema},
    },
    summary="Полное обновление самосвала по ID",
)
async def put_dump_truck(
    truck_in: DumpTruckCreateSchema,
    truck_id: int = Path(default=..., ge=1),
    db: AsyncSession = Depends(get_db),
):
    try:
        existing_truck = await db.get(DumpTruck, truck_id)
        if not existing_truck:
            return api_response.error(
                error="TruckNotFound",
                message=f"Самосвал с ID {truck_id} не найден",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        updated_truck = await update_truck(db, existing_truck, truck_in)
        return api_response.success(data=updated_truck)
    except TruckModelNotFoundError as e:
        return api_response.error(
            error="ModelNotFound",
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except DuplicateBoardNumberError as e:
        return api_response.error(
            error="DuplicateBoardNumber",
            message=str(e),
            status_code=status.HTTP_409_CONFLICT,
        )

# ──── DELETE ────
@trucks_router.delete(
    "/{truck_id}",
    response_model=ResponseSchema,
    responses={
        200: {"model": ResponseSchema},
        404: {"model": ErrorResponseSchema},
    },
    summary="Удалить самосвал по ID",
)
async def remove_dump_truck(
    truck_id: int = Path(default=..., ge=1),
    db: AsyncSession = Depends(get_db),
):
    existing_truck = await db.get(DumpTruck, truck_id)
    if not existing_truck:
        return api_response.error(
            error="TruckNotFound",
            message=f"Самосвал с ID {truck_id} не найден",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    await delete_truck(db, existing_truck)
    return api_response.success(data=None)
