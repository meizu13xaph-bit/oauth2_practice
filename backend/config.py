# Импортируем необходимые классы из библиотеки pydantic-settings
from pydantic_settings import BaseSettings, SettingsConfigDict


# Определяем класс Settings, который наследуется от BaseSettings.
# Это позволяет автоматически считывать переменные окружения.
class Settings(BaseSettings):
    # Секретный ключ клиента для Google OAuth.
    OAUTH_GOOGLE_CLIENT_SECRET: str
    # ID клиента для Google OAuth.
    OAUTH_GOOGLE_CLIENT_ID: str

    # Конфигурация модели Pydantic.
    # Указываем, что переменные нужно загружать из файла .env.
    model_config = SettingsConfigDict(env_file=".env")


# Создаем единственный экземпляр настроек, который будет использоваться
# во всем приложении.
settings = Settings()
