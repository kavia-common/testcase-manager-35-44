# Integration Notes

- Configure environment via .env:
  - POSTGRES_URL or individual POSTGRES_* variables (user, password, host, port, db)
  - FRONTEND_ORIGIN and ALLOWED_ORIGINS for CORS (comma-separated)
  - APP_PORT (default 3001)
- Database container (robot_database) applies migrations before backend connects.
- API base URL for frontend: set REACT_APP_API_BASE in robot_frontend/.env to http://localhost:3001
- API paths are unprefixed (e.g., /testcases, /scenarios, /runs, /logs/...).
