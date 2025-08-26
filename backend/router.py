# Импортируем необходимые типы и классы из FastAPI и других библиотек
import json
import base64
from typing import Annotated
from fastapi import APIRouter, Body, Request
from fastapi.responses import RedirectResponse

import aiohttp  # Для асинхронных HTTP-запросов
import jwt  # Для декодирования JWT-токена

from state_storage import state_storage  # Хранилище для проверки state
from oauth_google import generate_google_oauth_redirect_uri  # Генерация OAuth-ссылки
from config import settings  # Конфиг с секретами

# Создаем роутер с префиксом /auth для авторизации ggg
router = APIRouter(prefix="/auth")


# Эндпоинт для получения OAuth-ссылки Google
@router.get("/google/url")
def get_google_oauth_redirect_uri():
    # Генерируем ссылку для авторизации через Google
    uri = generate_google_oauth_redirect_uri()
    # Перенаправляем пользователя на эту ссылку
    return RedirectResponse(url=uri, status_code=302)


# Эндпоинт для обработки callback от Google после авторизации
@router.get("/google/callback")
async def handle_google_callback(request: Request):
    # Получаем code и state из query параметров
    code = request.query_params.get('code')
    state = request.query_params.get('state')

    # Проверяем, что state был ранее сгенерирован и сохранен
    if state not in state_storage:
        raise Exception("Invalid state") # Если state не найден — ошибка (можно добавить кастомные исключение)
    else:
        print("Стейт корректный")
    # URL для обмена кода на токен
    google_token_url = "https://oauth2.googleapis.com/token"

    # Асинхронно отправляем POST-запрос для получения токенов
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url=google_token_url,
            data={
                "client_id": settings.OAUTH_GOOGLE_CLIENT_ID,  # ID клиента из настроек
                "client_secret": settings.OAUTH_GOOGLE_CLIENT_SECRET,  # Секрет клиента
                "grant_type": "authorization_code",  # Тип запроса
                "redirect_uri": "http://localhost:8000/auth/google/callback",  # Должен совпадать с тем, что в Google Console
                "code": code,  # Код авторизации
            },
            ssl=False,
        ) as response:
            res = await response.json()  # Получаем ответ в формате JSON
            print(f"{res=}")
            id_token = res["id_token"]  # JWT-токен с данными пользователя
            access_token = res["access_token"]  # Токен доступа к API Google
            # Декодируем id_token для получения информации о пользователе
            user_data = jwt.decode(
                id_token,
                algorithms=["RS256"],
                options={"verify_signature": False},  # Без проверки подписи (для демо)
            )

    # Получаем список файлов пользователя из Google Drive
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url="https://www.googleapis.com/drive/v3/files",
            headers={"Authorization": f"Bearer {access_token}"},
            ssl=False,
        ) as response:
            res = await response.json()  # Получаем список файлов
            print(f"{res=}")
            files = [item["name"] for item in res.get("files", [])]  # Извлекаем имена файлов

    # Готовим данные для передачи на фронтенд
    frontend_data = {
        "user": user_data,
        "files": files,
    }

    # Кодируем данные в Base64
    json_data = json.dumps(frontend_data).encode('utf-8')
    token = base64.b64encode(json_data).decode('utf-8')

    # Перенаправляем пользователя на фронтенд с токеном
    return RedirectResponse(url=f"http://localhost:3000/auth/google?token={token}")
