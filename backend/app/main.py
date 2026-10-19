from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database.session import get_db
from app.routers import (
    audit_logs,
    auth,
    check_ins,
    clients,
    employees,
    payments,
    positions,
    reservations,
    room_categories,
    rooms,
    stay_history,
)


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(positions.router)
app.include_router(room_categories.router)
app.include_router(rooms.router)
app.include_router(employees.router)
app.include_router(reservations.router)
app.include_router(payments.router)
app.include_router(check_ins.router)
app.include_router(stay_history.router)
app.include_router(audit_logs.router)


@app.get("/")
async def root():
    return {
        "message": "Hotel API is running"
    }


@app.get("/health/db")
async def check_db(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        value = result.scalar()

        if value == 1:
            return {
                "status": "success",
                "message": "Database connection successful",
                "database": settings.DB_NAME,
            }

        return {
            "status": "error",
            "message": "Unexpected database response",
        }

    except Exception as e:
        return {
            "status": "error",
            "message": "Database connection failed",
            "detail": str(e),
        }