from typing import List, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.crud.truck_model import (
    create_model, get_model_by_id, get_models_list, update_model, delete_model
)
from app.schemas import TruckModelCreateSchema
from app.db.models import ModelTruck, DumpTruck
from app.schemas.services import ModelInUseError


class TruckModelService:
    """ Сервисный слой для работы с моделями самосвалов """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_model(self, model_id: int) -> ModelTruck:
        """ Получить модель по ID """
        return await get_model_by_id(self.db, model_id)

    async def get_models(
            self,
            skip: int = 0,
            limit: int = 100
    ) -> Tuple[List[ModelTruck], int]:
        """ Получить список моделей с пагинацией """
        return await get_models_list(
            db=self.db,
            skip=skip,
            limit=limit
        )

    async def create_model(self, model_data: TruckModelCreateSchema) -> ModelTruck:
        """ Создать новую модель самосвала """
        return await create_model(self.db, model_data)

    async def update_model(self, model_id: int, model_data: TruckModelCreateSchema) -> ModelTruck:
        """ Обновить модель самосвала """
        existing_model = await self.get_model(model_id)
        return await update_model(self.db, existing_model, model_data)

    async def delete_model(self, model_id: int) -> None:
        """ Удалить модель самосвала """
        existing_model = await self.get_model(model_id)
        if await self._has_trucks(model_id):
            raise ModelInUseError("Нельзя удалить модель, используемую самосвалами")

        await delete_model(self.db, existing_model)

    async def _has_trucks(self, model_id: int) -> bool:
        """ Проверить, используется ли модель самосвалами """
        stmt = select(DumpTruck.id).where(DumpTruck.model_id == model_id).limit(1)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
