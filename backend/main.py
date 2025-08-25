"""
Главный файл приложения (entrypoint).
Этот файл отвечает за создание и конфигурацию экземпляра веб-приложения FastAPI.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Импортируем 'router' из файла router.py. В нем определены все пути (эндпоинты) нашего API.
from router import router

# Создаем экземпляр FastAPI. 'app' будет являться основным объектом,
# управляющим всем API. FastAPI - это современный и быстрый веб-фреймворк для создания API на Python.
app = FastAPI(
    title="Google OAuth Demo App",
    description="Пример приложения, демонстрирующего аутентификацию через Google.",
    version="1.0.0",
)

# Подключаем роутер к нашему приложению. Это позволяет выносить определения
# эндпоинтов в отдельные файлы (модули), что делает код более чистым и организованным.
# Все эндпоинты из 'router' теперь будут доступны в нашем приложении.
app.include_router(router)

# Добавляем "промежуточный слой" (Middleware) для обработки CORS.
# CORS (Cross-Origin Resource Sharing) - это механизм безопасности, встроенный в браузеры,
# который по умолчанию блокирует запросы с одного домена (например, frontend на localhost:3000)
# на другой (например, backend на localhost:8000).
# Эта конфигурация "говорит" браузеру, что такие запросы безопасны и разрешены.
app.add_middleware(
    CORSMiddleware,
    # 'allow_origins': список доменов, с которых разрешены запросы.
    # Здесь мы разрешаем запросы только от нашего фронтенда.
    allow_origins=["http://localhost:3000"],
    # 'allow_credentials': разрешает отправку cookie в запросах. Это необходимо для
    # сессий или аутентификации на основе cookie.
    allow_credentials=True,
    # 'allow_methods': список разрешенных HTTP-методов. ["*"] означает "все методы" (GET, POST, PUT и т.д.).
    allow_methods=["*"],
    # 'allow_headers': список разрешенных HTTP-заголовков. ["*"] означает "все заголовки".
    allow_headers=["*"],
)