from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Импортируем роутер из соседнего файла router.py
from router import router

# Создаем экземпляр приложения FastAPI
app = FastAPI()

# Подключаем роутер к приложению. Все маршруты, определенные в 'router',
# станут частью нашего приложения.
app.include_router(router)

# Добавляем Middleware для обработки CORS (Cross-Origin Resource Sharing).
# Это необходимо, чтобы наш frontend, запущенный на другом домене/порту (localhost:3000),
# мог безопасно отправлять запросы к нашему backend (localhost:8000).
app.add_middleware(
    CORSMiddleware,
    # Указываем, с каких источников разрешены запросы.
    allow_origins=["http://localhost:3000"],
    # Разрешаем передачу cookie.
    allow_credentials=True,
    # Разрешаем все HTTP-методы (GET, POST, и т.д.).
    allow_methods=["*"],
    # Разрешаем все заголовки.
    allow_headers=["*"],
)