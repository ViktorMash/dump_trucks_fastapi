from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.crud import get_truck_by_id, get_trucks_list, create_truck, update_truck, delete_truck
from app.schemas import DumpTruckCreateSchema
from app.db.models import DumpTruck


class TruckService:
    """ Сервисный слой для работы с самосвалами """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_truck(self, truck_id: int) -> DumpTruck:
        """ Получить самосвал по ID """
        return await get_truck_by_id(self.db, truck_id)

    async def get_trucks(
            self,
            board_number: str = None,
            model_name: str = None,
            skip: int = 0,
            limit: int = 50
    ) -> Tuple[List[DumpTruck], int]:
        """ Получить список самосвалов с фильтрацией и пагинацией"""
        return await get_trucks_list(
            db=self.db,
            board_number=board_number,
            model_name=model_name,
            skip=skip,
            limit=limit
        )

    async def create_truck(self, truck_data: DumpTruckCreateSchema) -> DumpTruck:
        """ Создать новый самосвал """
        return await create_truck(self.db, truck_data)

    async def update_truck(self, truck_id: int, truck_data: DumpTruckCreateSchema) -> DumpTruck:
        """ Обновить самосвал """
        existing_truck = await self.get_truck(truck_id)
        return await update_truck(self.db, existing_truck, truck_data)

    async def delete_truck(self, truck_id: int) -> None:
        """ Удалить самосвал """
        existing_truck = await self.get_truck(truck_id)
        await delete_truck(self.db, existing_truck)
