from functools import lru_cache
from pydantic import BaseModel, Field
import os


class Settings(BaseModel):
    """Application settings loaded from environment variables."""

    # Database settings - required via environment (.env injected by orchestrator)
    POSTGRES_URL: str = Field(default="")
    POSTGRES_USER: str = Field(default="")
    POSTGRES_PASSWORD: str = Field(default="")
    POSTGRES_DB: str = Field(default="")
    POSTGRES_PORT: str = Field(default="5432")

    # CORS
    CORS_ORIGINS: str = Field(default="http://localhost:3000,https://vscode-internal-41361-beta.beta01.cloud.kavia.ai:3000")
    # Backward-compat aliases (if provided, fold into CORS_ORIGINS)
    FRONTEND_ORIGIN: str = Field(default="")
    ALLOWED_ORIGINS: str = Field(default="")

    # App
    APP_NAME: str = Field(default="Robot Framework Test Manager API")
    APP_VERSION: str = Field(default="0.1.0")
    APP_DESCRIPTION: str = Field(
        default=(
            "FastAPI backend for managing Robot Framework testcases, scenarios, "
            "groups, executions, run history, logs, and configurations."
        )
    )
    APP_PORT: int = Field(default=3001)

    def database_dsn(self) -> str:
        """Build an asyncpg SQLAlchemy DSN from discrete POSTGRES_* vars if POSTGRES_URL is not provided."""
        if self.POSTGRES_URL:
            # Allow providing a full DSN directly; ensure it's asyncpg-compatible
            url = self.POSTGRES_URL
            if url.startswith("postgresql://") and "+asyncpg" not in url:
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            return url

        user = os.getenv("POSTGRES_USER", self.POSTGRES_USER)
        password = os.getenv("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", self.POSTGRES_PORT)
        db = os.getenv("POSTGRES_DB", self.POSTGRES_DB)

        # Do not include password section if it's empty to avoid malformed URLs
        auth = user if password == "" else f"{user}:{password}"
        if not user and not password:
            auth = ""

        if auth:
            return f"postgresql+asyncpg://{auth}@{host}:{port}/{db}"
        return f"postgresql+asyncpg://{host}:{port}/{db}"

    def resolved_cors_origins(self) -> str:
        """Combine legacy FRONTEND_ORIGIN/ALLOWED_ORIGINS with CORS_ORIGINS."""
        parts = []
        for raw in [self.CORS_ORIGINS, self.FRONTEND_ORIGIN, self.ALLOWED_ORIGINS]:
            if raw:
                parts.extend([p.strip() for p in raw.split(",") if p.strip()])
        # preserve order and de-dupe
        seen = set()
        unique = []
        for p in parts:
            if p not in seen:
                seen.add(p)
                unique.append(p)
        return ",".join(unique) or "http://localhost:3000"


@lru_cache()
def get_settings() -> Settings:
    """Load settings with environment overrides."""
    return Settings(
        POSTGRES_URL=os.getenv("POSTGRES_URL", ""),
        POSTGRES_USER=os.getenv("POSTGRES_USER", ""),
        POSTGRES_PASSWORD=os.getenv("POSTGRES_PASSWORD", ""),
        POSTGRES_DB=os.getenv("POSTGRES_DB", ""),
        POSTGRES_PORT=os.getenv("POSTGRES_PORT", "5432"),
        CORS_ORIGINS=os.getenv("CORS_ORIGINS", os.getenv("ALLOWED_ORIGINS", os.getenv("FRONTEND_ORIGIN", "http://localhost:3000"))),
        FRONTEND_ORIGIN=os.getenv("FRONTEND_ORIGIN", ""),
        ALLOWED_ORIGINS=os.getenv("ALLOWED_ORIGINS", ""),
        APP_NAME=os.getenv("APP_NAME", "Robot Framework Test Manager API"),
        APP_VERSION=os.getenv("APP_VERSION", "0.1.0"),
        APP_DESCRIPTION=os.getenv(
            "APP_DESCRIPTION",
            "FastAPI backend for managing Robot Framework testcases, scenarios, groups, executions, run history, logs, and configurations.",
        ),
        APP_PORT=int(os.getenv("APP_PORT", "3001")),
    )
