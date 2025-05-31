from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.services import TruckService, TruckModelService


async def get_truck_service(db: AsyncSession = Depends(get_db)) -> TruckService:
    """ Провайдер для TruckService """
    return TruckService(db)


async def get_truck_model_service(db: AsyncSession = Depends(get_db)) -> TruckModelService:
    """ Провайдер для TruckModelService """
    return TruckModelService(db)