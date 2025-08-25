# Импортируем необходимые библиотеки и модули
from typing import Annotated
from fastapi import APIRouter, Body
from fastapi.responses import RedirectResponse

import aiohttp  # Для выполнения асинхронных HTTP-запросов
import jwt      # Для работы с JSON Web Tokens

from state_storage import state_storage  # Хранилище для state-токенов (защита от CSRF)
from oauth_google import generate_google_oauth_redirect_uri  # Функция для создания URL аутентификации
from config import settings  # Настройки приложения (client_id, client_secret)

# Создаем экземпляр APIRouter. Все пути, определенные здесь, будут иметь префикс /auth
router = APIRouter(prefix="/auth")


# Определяем GET-эндпоинт для получения URL для редиректа на страницу входа Google
@router.get("/google/url")
def get_google_oauth_redirect_uri():
    """
    Этот эндпоинт генерирует и возвращает URL для старта процесса аутентификации Google.
    Фронтенд должен перенаправить пользователя по этому URL.
    """
    uri = generate_google_oauth_redirect_uri()
    # Возвращаем ответ-перенаправление (HTTP 302)
    return RedirectResponse(url=uri, status_code=302)


# Определяем POST-эндпоинт, на который Google перенаправит пользователя после аутентификации
@router.post("/google/callback")
async def handle_code(
    # Получаем 'code' и 'state' из тела POST-запроса
    code: Annotated[str, Body()],
    state: Annotated[str, Body()],
):
    """
    Этот эндпоинт обрабатывает callback от Google.
    Он обменивает полученный 'code' на 'access_token' и 'id_token'.
    """
    # Проверяем, что полученный 'state' совпадает с тем, что мы сгенерировали ранее
    if state not in state_storage:
        # Если state не найден, это может быть попыткой CSRF-атаки
        raise Exception("Неверный state-токен.")
    else:
        print("Стейт корректный")

    google_token_url = "https://oauth2.googleapis.com/token"

    # Используем aiohttp для асинхронного POST-запроса к Google для обмена кода на токен
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url=google_token_url,
            data={
                "client_id": settings.OAUTH_GOOGLE_CLIENT_ID,
                "client_secret": settings.OAUTH_GOOGLE_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "redirect_uri": "http://localhost:3000/auth/google",
                "code": code,
            },
            # ssl=False - это небезопасно для продакшена, отключает проверку SSL-сертификата
            ssl=False,
        ) as response:
            # Получаем ответ от Google в формате JSON
            res = await response.json()
            print(f"{res=}")
            id_token = res["id_token"]        # Токен с информацией о пользователе
            access_token = res["access_token"]  # Токен для доступа к API Google

            # ---!!! КРИТИЧЕСКАЯ УЯЗВИМОСТЬ БЕЗОПАСНОСТИ !!!---
            # Декодирование JWT (id_token) без проверки подписи.
            # options={"verify_signature": False} означает, что мы доверяем любым данным в токене,
            # даже если он подделан. В реальном приложении так делать НЕЛЬЗЯ.
            # Необходимо загрузить публичные ключи Google и проверить подпись токена.
            user_data = jwt.decode(
                id_token,
                algorithms=["RS256"],
                options={"verify_signature": False},
            )

    # Используем полученный access_token для запроса к Google Drive API
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url="https://www.googleapis.com/drive/v3/files",
            headers={
                "Authorization": f"Bearer {access_token}"
            },
            ssl=False,
        ) as response:
            res = await response.json()
            print(f"{res=}")
            # Извлекаем только имена файлов из ответа API
            files = [item["name"] for item in res["files"]]

    # Возвращаем на фронтенд данные пользователя и список его файлов
    return {
        "user": user_data,
        "files": files,
    }