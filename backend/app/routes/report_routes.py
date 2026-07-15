from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from typing import Optional
from datetime import date as dt_date
import asyncpg

from app.database import get_db
from app.auth import get_current_user
from app.services.pdf_service import generate_attendance_pdf

router = APIRouter()


@router.get("/class/daily")
async def class_daily_report(
    class_id: str = Query(...),
    date: dt_date = Query(...),
    db: asyncpg.Pool = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    pdf = await generate_attendance_pdf(db, "class_daily", class_id=class_id, date=date)
    return StreamingResponse(pdf, media_type="application/pdf",
                             headers={"Content-Disposition": f"attachment; filename=class_daily_{date}.pdf"})


@router.get("/class/monthly")
async def class_monthly_report(
    class_id: str = Query(...),
    month: int = Query(..., ge=1, le=12),
    year: int = Query(...),
    db: asyncpg.Pool = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    pdf = await generate_attendance_pdf(db, "class_monthly", class_id=class_id, month=month, year=year)
    return StreamingResponse(pdf, media_type="application/pdf",
                             headers={"Content-Disposition": f"attachment; filename=class_monthly_{year}_{month}.pdf"})


@router.get("/class/annual")
async def class_annual_report(
    class_id: str = Query(...),
    academic_year_id: str = Query(...),
    db: asyncpg.Pool = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    pdf = await generate_attendance_pdf(db, "class_annual", class_id=class_id, academic_year_id=academic_year_id)
    return StreamingResponse(pdf, media_type="application/pdf",
                             headers={"Content-Disposition": "attachment; filename=class_annual.pdf"})


@router.get("/school/daily")
async def school_daily_report(
    date: dt_date = Query(...),
    db: asyncpg.Pool = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    pdf = await generate_attendance_pdf(db, "school_daily", date=date)
    return StreamingResponse(pdf, media_type="application/pdf",
                             headers={"Content-Disposition": f"attachment; filename=school_daily_{date}.pdf"})


@router.get("/school/monthly")
async def school_monthly_report(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(...),
    db: asyncpg.Pool = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    pdf = await generate_attendance_pdf(db, "school_monthly", month=month, year=year)
    return StreamingResponse(pdf, media_type="application/pdf",
                             headers={"Content-Disposition": f"attachment; filename=school_monthly_{year}_{month}.pdf"})


@router.get("/school/annual")
async def school_annual_report(
    academic_year_id: str = Query(...),
    db: asyncpg.Pool = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    pdf = await generate_attendance_pdf(db, "school_annual", academic_year_id=academic_year_id)
    return StreamingResponse(pdf, media_type="application/pdf",
                             headers={"Content-Disposition": "attachment; filename=school_annual.pdf"})


@router.get("/class/{class_id}/students-on-date")
async def class_students_on_date(
    class_id: str,
    date: str = Query(...),
    db: asyncpg.Pool = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    """Returns present/absent student list for the class detail modal (JSON, not PDF)."""
    cls = await db.fetchrow(
        "SELECT grade, medium, gender_type FROM classes WHERE id = $1", class_id
    )
    if not cls:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Class not found")

    class_name = f"Grade {cls['grade']} {cls['medium']} {cls['gender_type']}"

    rows = await db.fetch(
        """SELECT s.id, s.registration_number, s.full_name, s.gender, a.status
           FROM attendance a
           JOIN students s ON a.student_id = s.id
           WHERE a.class_id = $1 AND a.attendance_date = $2
           ORDER BY s.full_name""",
        class_id, date,
    )

    students = [
        {
            "student_id": str(r["id"]),
            "registration_number": r["registration_number"],
            "full_name": r["full_name"],
            "gender": r["gender"],
            "status": r["status"],
        }
        for r in rows
    ]

    present = sum(1 for r in rows if r["status"] == "Present")
    absent = len(rows) - present
    pct = round((present / len(rows)) * 100, 1) if rows else 0.0

    return {
        "class_id": class_id,
        "class_name": class_name,
        "date": date,
        "students": students,
        "present": present,
        "absent": absent,
        "percentage": pct,
    }
