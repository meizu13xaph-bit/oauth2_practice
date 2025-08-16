from typing import Annotated
from fastapi import APIRouter, Body
from fastapi.responses import RedirectResponse

import aiohttp
import jwt

from state_storage import state_storage
from oauth_google import generate_google_oauth_redirect_uri
from config import settings

# Создаем роутер с префиксом /auth. Все пути в этом файле будут начинаться с /auth.
router = APIRouter(prefix="/auth")


# Шаг 1: Получение URL для перенаправления пользователя на страницу входа Google.
@router.get("/google/url")
def get_google_oauth_redirect_uri():
    """
    Этот эндпоинт вызывается, когда пользователь нажимает кнопку "Войти через Google" на фронтенде.
    """
    # Генерируем URL для OAuth 2.0 аутентификации Google.
    uri = generate_google_oauth_redirect_uri()
    # Возвращаем ответ-перенаправление (HTTP 302) на сгенерированный URL.
    return RedirectResponse(url=uri, status_code=302)


# Шаг 2: Обработка коллбэка от Google после успешной аутентификации.
@router.post("/google/callback")
async def handle_code(
    # FastAPI автоматически извлекает 'code' и 'state' из тела POST-запроса.
    code: Annotated[str, Body()],
    state: Annotated[str, Body()],
):
    """
    Этот эндпоинт вызывается фронтендом после того, как Google перенаправил
    пользователя обратно в приложение с параметрами 'code' и 'state'.
    """
    # Проверка безопасности: убеждаемся, что 'state' совпадает с тем, что мы отправляли.
    if state not in state_storage:
        raise Exception("Invalid state") # В реальном приложении здесь должна быть более качественная обработка ошибок.
    else:
        print("Стейт корректный")

    # URL для обмена кода авторизации на токен доступа.
    google_token_url = "https://oauth2.googleapis.com/token"

    # Шаг 2.1: Обмен кода на токен доступа (access token) и ID токен.
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url=google_token_url,
            data={
                "client_id": settings.OAUTH_GOOGLE_CLIENT_ID,
                "client_secret": settings.OAUTH_GOOGLE_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "redirect_uri": "http://localhost:3000/auth/google", # Должен совпадать с указанным в Google Cloud Console.
                "code": code,
            },
            ssl=False, # В реальном приложении ssl=True является обязательным для безопасности.
        ) as response:
            res = await response.json()
            print(f"{res=}")
            id_token = res["id_token"] # Токен с информацией о пользователе.
            access_token = res["access_token"] # Токен для доступа к API Google.

            # Шаг 2.2: Декодирование ID токена для получения информации о пользователе.
            # Внимание: verify_signature=False используется только для примера.
            # В реальном приложении необходимо верифицировать подпись, чтобы убедиться,
            # что токен действительно пришел от Google.
            user_data = jwt.decode(
                id_token,
                algorithms=["RS256"],
                options={"verify_signature": False},
            )

    # Шаг 2.3: Использование access_token для запроса к Google Drive API.
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url="https://www.googleapis.com/drive/v3/files",
            headers={
                "Authorization": f"Bearer {access_token}" # Передаем токен в заголовке.
            },
            ssl=False, # В реальном приложении ssl=True является обязательным.
        ) as response:
            res = await response.json()
            print(f"{res=}")
            # Извлекаем только имена файлов из ответа API.
            files = [item["name"] for item in res["files"]]

    # Шаг 2.4: Возвращаем данные на фронтенд.
    return {
        "user": user_data,
        "files": files,
    }