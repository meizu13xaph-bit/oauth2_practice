# Импортируем FastAPI и middleware для поддержки CORS
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from router import router  # Импортируем роутер с эндофитами авторизации


# Создаем экземпляр FastAPI приложения
app = FastAPI()

# Подключаем роутер с префиксом /auth
app.include_router(router)
# Добавляем middleware для поддержки CORS (разрешаем запросы с фронтенда)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Разрешаем только локальный фронтенд
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
