from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import get_pool, close_pool
from app.routes import (
    auth_routes,
    academic_year_routes,
    class_routes,
    student_routes,
    attendance_routes,
    report_routes,
    import_routes,
    promotion_routes,
    teacher_routes,
    audit_routes,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create DB pool
    await get_pool()
    yield
    # Shutdown: close DB pool
    await close_pool()


app = FastAPI(
    title="Ahadiya School Management System API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
settings = get_settings()
origins = [o.strip() for o in settings.cors_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_routes.router, prefix="/api/auth", tags=["Auth"])
app.include_router(academic_year_routes.router, prefix="/api/academic-years", tags=["Academic Years"])
app.include_router(class_routes.router, prefix="/api/classes", tags=["Classes"])
app.include_router(student_routes.router, prefix="/api/students", tags=["Students"])
app.include_router(attendance_routes.router, prefix="/api/attendance", tags=["Attendance"])
app.include_router(report_routes.router, prefix="/api/reports", tags=["Reports"])
app.include_router(import_routes.router, prefix="/api/import", tags=["Import"])
app.include_router(promotion_routes.router, prefix="/api/promotion", tags=["Promotion"])
app.include_router(teacher_routes.router, prefix="/api/teachers", tags=["Teachers"])
app.include_router(audit_routes.router, prefix="/api/audit-logs", tags=["Audit Logs"])


@app.api_route("/api/health", methods=["GET", "HEAD"])
async def health_check():
    return {"status": "ok", "service": "ahadiya-backend"}
