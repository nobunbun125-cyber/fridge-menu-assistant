import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anthropic_api_key: str = ""
    anthropic_model_planning: str = "claude-sonnet-5"
    anthropic_model_light: str = "claude-haiku-4-5-20251001"

    database_url: str = "sqlite:///./app.db"
    database_require_ssl: bool = False

    jwt_secret_key: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


def _load_secrets_from_ssm(settings: Settings) -> None:
    """Lambda実行時のみ、SSM Parameter Storeからシークレットを読み取り、settingsを上書きする。

    ローカル開発では SSM_PARAMETER_PREFIX が未設定のため、この関数は何もしない。
    DB接続情報はホスト名等(非秘密)を環境変数で渡し、パスワードだけSSMから取得して組み立てる。
    """
    prefix = os.environ.get("SSM_PARAMETER_PREFIX")
    if not prefix:
        return

    import boto3

    ssm = boto3.client("ssm")

    def _get(name: str) -> str:
        response = ssm.get_parameter(Name=f"{prefix}/{name}", WithDecryption=True)
        return response["Parameter"]["Value"]

    settings.anthropic_api_key = _get("anthropic_api_key")
    settings.jwt_secret_key = _get("jwt_secret_key")

    db_password = _get("db_master_password")
    settings.database_url = (
        f"postgresql+pg8000://{os.environ['DB_USERNAME']}:{db_password}"
        f"@{os.environ['DB_HOST']}:{os.environ.get('DB_PORT', '5432')}/{os.environ['DB_NAME']}"
    )
    settings.database_require_ssl = True


settings = Settings()
_load_secrets_from_ssm(settings)
