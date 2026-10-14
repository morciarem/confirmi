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

email_settings = EmailSettings()



settings = Settings()