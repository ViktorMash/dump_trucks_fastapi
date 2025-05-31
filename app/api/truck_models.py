from fastapi import APIRouter, Depends, Path, Query, status, Request

from .response_api import api_response
from app.schemas import TruckModelCreateSchema
from app.schemas.http_response import ResponseSchema, ErrorResponseSchema
from app.services import TruckModelService
from app.dependencies import get_truck_model_service
from app.schemas.http_response import ModelNotFoundError, DuplicateModelNameError
from app.schemas.services import ModelInUseError

truck_models_router = APIRouter(
    prefix="/models",
    tags=["Модели самосвалов"],
)


# ──── CREATE ────
@truck_models_router.post(
    "/",
    response_model=ResponseSchema,
    responses={
        201: {"model": ResponseSchema},
        404: {"model": ErrorResponseSchema},
        409: {"model": ErrorResponseSchema},
    },
    summary="Добавить новую модель самосвала в БД",
    status_code=status.HTTP_201_CREATED,
)
async def add_truck_model(
        model_in: TruckModelCreateSchema,
        model_service: TruckModelService = Depends(get_truck_model_service),
):
    try:
        model = await model_service.create_model(model_in)
        return api_response.success(
            data=model,
            status_code=status.HTTP_201_CREATED,
        )

    except DuplicateModelNameError as e:
        return api_response.error(
            error=f"Модель уже существует в БД",
            message=str(e),
            status_code=status.HTTP_409_CONFLICT,
        )


# ──── READ (список моделей) ────
@truck_models_router.get(
    "/",
    response_model=ResponseSchema,
    responses={
        200: {"model": ResponseSchema},
        404: {"model": ErrorResponseSchema},
    },
    summary="Получить список моделей самосвалов",
)
async def list_truck_models(
        request: Request,
        page: int = Query(default=1, ge=1, description="Номер страницы"),
        per_page: int = Query(default=100, ge=1, le=100, description="Количество записей на странице"),
        model_service: TruckModelService = Depends(get_truck_model_service),
):
    skip = (page - 1) * per_page

    models, total_count = await model_service.get_models(
        skip=skip,
        limit=per_page
    )

    return api_response.success(
        data=models,
        total=total_count,
        page=page,
        per_page=per_page,
        request=request,
    )


# ──── READ (одна модель) ────
@truck_models_router.get(
    "/{model_id}",
    response_model=ResponseSchema,
    responses={
        200: {"model": ResponseSchema},
        404: {"model": ErrorResponseSchema},
    },
    summary="Получить данные модели по ID",
)
async def get_truck_model(
        model_id: int = Path(default=..., ge=1),
        model_service: TruckModelService = Depends(get_truck_model_service),
):
    try:
        model = await model_service.get_model(model_id)
        return api_response.success(data=model)

    except ModelNotFoundError as e:
        return api_response.error(
            error=f"Модель с ID:{model_id} не найдена",
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND,
        )


# ──── UPDATE ────
@truck_models_router.put(
    "/{model_id}",
    response_model=ResponseSchema,
    responses={
        200: {"model": ResponseSchema},
        404: {"model": ErrorResponseSchema},
        409: {"model": ErrorResponseSchema},
    },
    summary="Обновить данные модели по ID",
)
async def update_truck_model(
        model_in: TruckModelCreateSchema,
        model_id: int = Path(default=..., ge=1),
        model_service: TruckModelService = Depends(get_truck_model_service),
):
    try:
        updated_model = await model_service.update_model(model_id, model_in)
        return api_response.success(data=updated_model)

    except ModelNotFoundError as e:
        return api_response.error(
            error=f"Модель с ID:{model_id} не найдена",
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except DuplicateModelNameError as e:
        return api_response.error(
            error="Модель уже существует в БД",
            message=str(e),
            status_code=status.HTTP_409_CONFLICT,
        )


@truck_models_router.delete(
    "/{model_id}",
    response_model=ResponseSchema,
    responses={
        200: {"model": ResponseSchema},
        404: {"model": ErrorResponseSchema},
        409: {"model": ErrorResponseSchema},
    },
    summary="Удалить модель самосвала",
)
async def delete_truck_model(
        model_id: int = Path(default=..., ge=1),
        model_service: TruckModelService = Depends(get_truck_model_service),
):
    try:
        await model_service.delete_model(model_id)
        return api_response.success(data=None)
    except ModelNotFoundError as e:
        return api_response.error(
            error=f"Модель с ID:{model_id} не найдена",
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND,
        )
    except ModelInUseError as e:
        return api_response.error(
            error=f"Модель с ID: {model_id} используется",
            message=str(e),
            status_code=status.HTTP_409_CONFLICT,
        )