from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from starlette.responses import JSONResponse

from app.core.init_test_data import init_test_data
from app.db.session import engine, Base, get_db, AsyncSessionLocal

from app.db.models import DumpTruck, ModelTruck
from app.api import trucks_router, truck_models_router
from app.config import settings

import uvicorn


async def initialize_test_data():
    """ Инициализация тестовых данных """
    try:
        async with AsyncSessionLocal() as session:
            await init_test_data(session)
    except Exception as e:
        print(f"Ошибка при инициализации тестовых данных: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Запуск приложения")
    # Создаём таблицы, если их ещё нет
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Инициализация тестовых данных
    await initialize_test_data()

    yield
    print("Остановка приложения")
    await engine.dispose()


app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description=settings.description,
    lifespan=lifespan
)


@app.get("/", include_in_schema=False)
def root():
    """ Переадресация на страницу docs """
    return RedirectResponse(url="/docs")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "data": None,
            "meta": {
                "status_code": 500,
                "message": "Internal server error",
                "details": str(exc) if settings.debug else "Внутренняя ошибка сервера"
            }
        }
    )

app.include_router(trucks_router, prefix=settings.api_prefix)
app.include_router(truck_models_router, prefix=settings.api_prefix)


if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )