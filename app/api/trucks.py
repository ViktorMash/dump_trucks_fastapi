from typing import Optional
from fastapi import APIRouter, Depends, Path, Query, status, Request

from .response_api import api_response
from app.schemas import DumpTruckCreateSchema
from app.schemas.http_response import ResponseSchema, ErrorResponseSchema
from app.services import TruckService
from app.dependencies import get_truck_service
from app.schemas.http_response import (
    TruckNotFoundError, TruckModelNotFoundError, DuplicateBoardNumberError
)

trucks_router = APIRouter(
    prefix="/trucks",
    tags=["Самосвалы"],
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
    truck_service: TruckService = Depends(get_truck_service),
):
    try:
        truck = await truck_service.create_truck(truck_in)
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
            error="Бортовой номер уже существует в БД",
            message=str(e),
            status_code=status.HTTP_409_CONFLICT,
        )

# ──── READ (список самосвалов) ────
@trucks_router.get(
    "/",
    response_model=ResponseSchema,
    responses={
        200: {"model": ResponseSchema},
        404: {"model": ErrorResponseSchema},
    },
    summary="Получить список самосвалов",
)
async def list_dump_trucks(
    request: Request,
    board_number: Optional[str] = Query(default=None, description="Фильтр по бортовому номеру"),
    model_name: Optional[str] = Query(default=None, description="Фильтр по модели"),
    page: int = Query(default=1, ge=1, description="Номер страницы"),
    per_page: int = Query(default=50, ge=1, le=100, description="Количество записей на странице"),
    truck_service: TruckService = Depends(get_truck_service),
):
    skip = (page - 1) * per_page

    trucks, total_count = await truck_service.get_trucks(
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


# ──── READ (один самосвал) ────
@trucks_router.get(
    "/{truck_id}",
    response_model=ResponseSchema,
    responses={
        200: {"model": ResponseSchema},
        404: {"model": ErrorResponseSchema},
    },
    summary="Получить данные самосвала по ID",
)
async def get_dump_truck(
    truck_id: int = Path(default=..., ge=1),
    truck_service: TruckService = Depends(get_truck_service),
):
    try:
        truck = await truck_service.get_truck(truck_id)
        return api_response.success(data=truck)

    except TruckNotFoundError as e:
        return api_response.error(
            error=f"Самосвал с ID:{truck_id} не найден",
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
    summary="Обновить данные самосвала по ID",
)
async def update_dump_truck(
    truck_in: DumpTruckCreateSchema,
    truck_id: int = Path(default=..., ge=1),
    truck_service: TruckService = Depends(get_truck_service),
):
    try:
        updated_truck = await truck_service.update_truck(truck_id, truck_in)
        return api_response.success(data=updated_truck)

    except TruckNotFoundError as e:
        return api_response.error(
            error=f"Самосвал с ID:{truck_id} не найден",
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except TruckModelNotFoundError as e:
        return api_response.error(
            error="Модель не найдена",
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except DuplicateBoardNumberError as e:
        return api_response.error(
            error="Бортовой номер уже существует в БД",
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
    truck_service: TruckService = Depends(get_truck_service),
):
    try:
        await truck_service.delete_truck(truck_id)
        return api_response.success(data=None)

    except TruckNotFoundError as e:
        return api_response.error(
            error=f"Самосвал с ID:{truck_id} не найден",
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND,
        )
