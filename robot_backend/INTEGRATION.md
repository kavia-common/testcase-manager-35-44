# Integration Notes

- Configure environment via .env:
  - POSTGRES_URL or individual POSTGRES_* variables (user, password, host, port, db)
  - FRONTEND_ORIGIN and ALLOWED_ORIGINS for CORS (comma-separated)
  - APP_PORT (default 3001)
- Database container (robot_database) applies migrations before backend connects.
- API base URL for frontend: set REACT_APP_API_BASE in robot_frontend/.env to http://localhost:3001
- API paths are unprefixed (e.g., /testcases, /scenarios, /runs, /logs/...).

## Running the backend locally

Recommended: run the FastAPI app using Python's module mode so `src` resolves as a package:

- Start with uvicorn:
  - uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload

- Or using Python's module execution:
  - python -m src.api.main

Avoid direct script execution (python src/api/main.py), which can cause `ModuleNotFoundError: No module named 'src'` depending on your working directory and PYTHONPATH.

```bash
# Example (development)
export APP_PORT=3001
export CORS_ORIGINS="http://localhost:3000"
# Set Postgres configuration via POSTGRES_URL or individual env vars
uvicorn src.api.main:app --host 0.0.0.0 --port ${APP_PORT:-3001} --reload
```

## Generating OpenAPI file

To regenerate interfaces/openapi.json based on the current app routes:

```bash
python -m src.api.generate_openapi
```

This ensures imports resolve correctly while generating the schema.
