import urllib.parse
import secrets

from state_storage import state_storage
from config import settings


def generate_google_oauth_redirect_uri():
    """
    Генерирует полный URL-адрес для перенаправления пользователя на страницу
    согласия Google OAuth 2.0.
    """
    # Создаем криптографически случайную строку 'state' для защиты от CSRF-атак.
    # CSRF (Cross-Site Request Forgery) - вид атаки на веб-пользователей.
    random_state = secrets.token_urlsafe(16)
    # Сохраняем 'state' во временное хранилище, чтобы проверить его на этапе коллбэка.
    state_storage.add(random_state)

    # Параметры запроса, которые будут отправлены в Google.
    query_params = {
        # ID нашего клиента, полученный в Google Cloud Console.
        "client_id": settings.OAUTH_GOOGLE_CLIENT_ID,
        # URL, на который Google перенаправит пользователя после аутентификации.
        "redirect_uri": "http://localhost:3000/auth/google",
        # Указываем, что мы запрашиваем код авторизации.
        "response_type": "code",
        # 'scope' определяет, к каким данным пользователя мы запрашиваем доступ.
        "scope": " ".join([
            "https://www.googleapis.com/auth/drive",  # Доступ к файлам на Google Drive
            "https://www.googleapis.com/auth/calendar", # Доступ к Google Calendar
            "openid", # Стандартный скоуп для OpenID Connect
            "profile", # Доступ к базовой информации профиля (имя, фото)
            "email", # Доступ к email адресу
        ]),
        # 'offline' означает, что мы можем получить refresh_token для долгосрочного доступа.
        "access_type": "offline",
        # Передаем сгенерированный 'state' для защиты от CSRF.
        "state": random_state,
    }

    # Кодируем параметры в строку запроса (например, 'key=value&key2=value2').
    query_string = urllib.parse.urlencode(query_params, quote_via=urllib.parse.quote)
    # Базовый URL для аутентификации Google.
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    # Собираем финальный URL.
    return f"{base_url}?{query_string}"
