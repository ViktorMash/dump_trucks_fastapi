from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.trucks import DumpTruck, ModelTruck


async def init_test_data(session: AsyncSession) -> None:
    """ Инициализация тестовых данных при первом запуске """

    # Проверяем, есть ли уже данные (без joined loads)
    result = await session.execute(select(ModelTruck.id))  # Берем только ID
    existing_models = result.scalars().all()

    if existing_models:
        print("Тестовые данные уже существуют, пропускаем инициализацию")
        return

    print("Создание тестовых данных...")

    # Создаем модели самосвалов
    models_data = [
        {"name": "БЕЛАЗ", "max_capacity": 120},
        {"name": "Komatsu", "max_capacity": 110},
    ]

    models = []
    for model_data in models_data:
        model = ModelTruck(**model_data)
        session.add(model)
        models.append(model)

    # Обязательно commit перед созданием самосвалов
    await session.commit()

    # Обновляем объекты, чтобы получить ID
    for model in models:
        await session.refresh(model)

    # Находим модели по именам для надежности
    belaz_model = next(m for m in models if m.name == "БЕЛАЗ")
    komatsu_model = next(m for m in models if m.name == "Komatsu")

    # Проверяем, нет ли уже самосвалов (только ID)
    truck_check = await session.execute(select(DumpTruck.id))
    existing_trucks = truck_check.scalars().all()

    if existing_trucks:
        print("Самосвалы уже существуют, пропускаем создание")
        return

    # Создаем самосвалы согласно заданию
    trucks_data = [
        {"board_number": "101", "current_weight": 100, "model_id": belaz_model.id},  # БЕЛАЗ - норма
        {"board_number": "102", "current_weight": 125, "model_id": belaz_model.id},  # БЕЛАЗ - перегруз 4.17%
        {"board_number": "K103", "current_weight": 120, "model_id": komatsu_model.id},  # Komatsu - перегруз 9.09%
    ]

    for truck_data in trucks_data:
        truck = DumpTruck(**truck_data)
        session.add(truck)

    await session.commit()
    print("Тестовые данные успешно созданы!")