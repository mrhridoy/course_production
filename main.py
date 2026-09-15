from contextlib import asynccontextmanager
import os
import traceback

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routes import (
    auth,
    users,
    categories,
    courses,
    enrollments,
    payments,
    dashboard,
    admin_settings,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Make sure upload subdirs exist; schema is owned by Alembic, NOT create_all.
    os.makedirs(f"{settings.UPLOAD_DIR}/thumbnails", exist_ok=True)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Course Management System API for ICT Bangladesh",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://localhost:3000",
        "http://localhost:3001",
        "https://localhost:3001",
        "http://localhost:5173",
        "https://localhost:5173",
        "https://student.ictbangladesh.bd",
        "http://student.ictbangladesh.bd",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global exception handler ──────────────────────────────────────────────────
# Starlette's CORSMiddleware only attaches Access-Control-Allow-Origin to
# responses it processes.  When an unhandled exception propagates past the
# middleware stack before a Response object exists, the header is never added
# and the browser reports a CORS error instead of the real 500.
#
# This handler catches every unhandled exception, logs the traceback, and
# returns a proper JSONResponse — which the CORS middleware CAN wrap.
@app.exception_handler(Exception)
async def _unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    traceback.print_exc()          # still visible in `docker compose logs`
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Check server logs for details."},
    )

# Serve uploaded files as static
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Register all routers
app.include_router(auth.router,            prefix="/api/v1/auth",           tags=["Auth"])
app.include_router(users.router,           prefix="/api/v1/users",          tags=["Users"])
app.include_router(categories.router,      prefix="/api/v1/categories",     tags=["Categories"])
app.include_router(courses.router,         prefix="/api/v1/courses",        tags=["Courses"])
app.include_router(enrollments.router,     prefix="/api/v1/enrollments",    tags=["Enrollments"])
app.include_router(payments.router,        prefix="/api/v1/payments",       tags=["Payments"])
app.include_router(dashboard.router,       prefix="/api/v1/dashboard",      tags=["Dashboard"])
app.include_router(admin_settings.router,  prefix="/api/v1/admin/settings", tags=["Admin Settings"])


@app.get("/", tags=["Health"])
def root():
    return {
        "message": "Welcome to ICT Bangladesh API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/healthz", tags=["Health"])
def healthz():
    return {"status": "ok"}
