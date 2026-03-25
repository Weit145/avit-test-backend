import logging
from .core.logging import setup_logging

from contextlib import asynccontextmanager
import uvicorn

from app.api.v1.auth import router as auth_router
from app.api.v1.rooms import router as room_router
from app.api.v1.bookings import router as booking_router
from fastapi import FastAPI, status


logger = logging.getLogger(__name__)
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Запуск приложения")
    yield
    logger.info("Остановка приложения")


app = FastAPI(
    lifespan=lifespan,
    title="Avito TEST",
    swagger_ui_parameters={"persistAuthorization": True},
)
app.include_router(auth_router)
app.include_router(room_router)
app.include_router(booking_router)


@app.get("/_info", status_code=status.HTTP_200_OK)
async def info():
    return status.HTTP_200_OK


if __name__ == "__main__":
    uvicorn.run("app.main:app", reload=True)
