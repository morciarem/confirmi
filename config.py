from pydantic_settings import BaseSettings, SettingsConfigDict

class EmailSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    sender_email: str = "morciarem@gmail.com"
    sender_password: str # pydantic will automatically read this from the .env file as SENDER_PASSWORD
    subject: str = "Verify your email"
    body: str = "Please verify your email address by clicking the link below:"
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    database_url: str 
    frontend_url: str
    signup_limit: str = "5/minute"
    
class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    secret_key: str
    access_token_minutes: int = 15
    refresh_token_days: int = 7
    algorithm: str = "HS256"

email_settings = EmailSettings()
auth_settings = AuthSettings()
settings = Settings()