from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.settings import get_settings
from src.routers.testcases import router as testcases_router
from src.routers.groups import router as groups_router
from src.routers.scenarios import router as scenarios_router
from src.routers.runs import router as runs_router
from src.routers.logs import router as logs_router
from src.routers.configs import router as configs_router

settings = get_settings()

openapi_tags = [
    {"name": "Testcases", "description": "CRUD operations for testcases."},
    {"name": "Groups", "description": "Manage groups and testcase associations."},
    {"name": "Scenarios", "description": "Manage scenarios and their inputs."},
    {"name": "Runs", "description": "Trigger and inspect execution runs."},
    {"name": "Logs", "description": "Access run logs and attachments."},
    {"name": "Configs", "description": "Manage key-value configuration."},
]

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    openapi_tags=openapi_tags,
)

# CORS
origins_csv = settings.resolved_cors_origins() if hasattr(settings, "resolved_cors_origins") else settings.CORS_ORIGINS
allowed_origins = [o.strip() for o in origins_csv.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Configs"], summary="Health Check")
def health_check():
    """Health check endpoint to verify service availability."""
    return {"message": "Healthy"}


# Include routers
app.include_router(testcases_router)
app.include_router(groups_router)
app.include_router(scenarios_router)
app.include_router(runs_router)
app.include_router(logs_router)
app.include_router(configs_router)
