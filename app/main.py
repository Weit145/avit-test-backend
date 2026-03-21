import logging
from .core.logging import setup_logging

from contextlib import asynccontextmanager
import uvicorn

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from fastapi import APIRouter

logger = logging.getLogger(__name__)
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Запуск приложения")
    yield
    logger.info("Остановка приложения")

app = FastAPI(lifespan=lifespan, title="Avito TEST")


if __name__ == "__main__":
    uvicorn.run("app.main:app", reload=True)