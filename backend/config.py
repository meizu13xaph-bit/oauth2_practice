# Импортируем базовые классы для работы с настройками из pydantic_settings
from pydantic_settings import BaseSettings, SettingsConfigDict


# Класс для хранения конфигурации приложения
class Settings(BaseSettings):
    OAUTH_GOOGLE_CLIENT_SECRET: str  # Секрет клиента Google OAuth (из .env)
    OAUTH_GOOGLE_CLIENT_ID: str  # ID клиента Google OAuth (из .env)

    # Указываем, что настройки берутся из файла .env
    model_config = SettingsConfigDict(env_file=".env")


# Создаем экземпляр настроек, который будет использоваться в приложении
settings = Settings()
