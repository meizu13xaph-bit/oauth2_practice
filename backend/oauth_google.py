# Импорт стандартных библиотек для работы с URL и генерации случайных строк
from config_log import ConfigLogger
logF = ConfigLogger.get_logger("OnlyFile")

import urllib.parse
import secrets

from state_storage import state_storage  # Импорт хранилища для state
from config import settings  # Импорт настроек с секретами


def generate_google_oauth_redirect_uri():
    # Генерируем случайную строку для защиты от CSRF-атак
    random_state = secrets.token_urlsafe(16)
    # Сохраняем state в хранилище для последующей проверки
    state_storage.add(random_state)

    # Формируем параметры запроса для OAuth авторизации Google
    query_params = {
        "client_id": settings.OAUTH_GOOGLE_CLIENT_ID,  # ID клиента из Google Console
        "redirect_uri": "http://localhost:8000/auth/google/callback",  # URL для возврата после авторизации
        "response_type": "code",  # Тип ответа — код авторизации
        "scope": " ".join(
            [
                "https://www.googleapis.com/auth/drive",  # Доступ к Google Drive
                "https://www.googleapis.com/auth/calendar",  # Доступ к Google Calendar
                "openid",  # OpenID для получения id_token
                "profile",  # Профиль пользователя
                "email",  # Email пользователя
            ]
        ),
        "access_type": "offline",  # Для получения refresh_token
        "state": random_state,  # State для защиты от CSRF
    }

    # Кодируем параметры в строку запроса
    query_string = urllib.parse.urlencode(query_params, quote_via=urllib.parse.quote)
    base_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"  # Базовый URL авторизации Google
    )
    # Возвращаем итоговую ссылку для авторизации
    return f"{base_url}?{query_string}"
