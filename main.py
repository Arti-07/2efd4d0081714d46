from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.config import settings
from src.database import init_database
from src.routes import auth_router, personality_router, astro_router, audio_router, vibe_router

import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Запуск приложения...")
    init_database()
    print("✅ Приложение готово к работе!")
    print("✅ перейдите на http://127.0.0.1:8000/")
    yield
    print("🛑 Остановка приложения...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend для AI-сервиса по выбору карьеры",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(personality_router)
app.include_router(astro_router)
app.include_router(vibe_router)
app.include_router(audio_router)


@app.get("/")
async def root():
    return {
        "message": "Career AI Backend API",
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected"
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)