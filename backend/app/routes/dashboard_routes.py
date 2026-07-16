import asyncio
from typing import Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends
import asyncpg

from app.database import get_db
from app.auth import get_current_user
from app.models import UserProfile, AcademicYearResponse, AttendanceSummary

router = APIRouter()

@router.get("/bootstrap")
async def dashboard_bootstrap(
    attendance_date: Optional[str] = None,
    db: asyncpg.Pool = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    """
    Combines User Profile, Current Academic Year, and Dashboard Summary into a single payload.
    This eliminates the 3 serial waterfall API requests on application load.
    """
    from app.cache import (
        cache_get, cache_set, get_current_year_id,
        TOTAL_STUDENTS, TOTAL_TEACHERS, TOTAL_CLASSES, CURRENT_YEAR, TOTAL_ALUMNIS,
    )

    if not attendance_date:
        # Find the most recent Sunday
        today = date.today()
        days_since_sunday = (today.weekday() + 1) % 7
        attendance_date = str(today if days_since_sunday == 0 else today.replace(
            day=today.day - days_since_sunday))

    parsed_date = datetime.strptime(
        attendance_date, "%Y-%m-%d").date() if isinstance(attendance_date, str) else attendance_date

    # Cached year ID is the foundation for all queries
    year_id = await get_current_year_id(db)

    # 1. Start defining tasks for asyncio.gather
    tasks = []
    task_keys = []

    # Task: Full User Profile
    tasks.append(db.fetchrow(
        """
        SELECT t.id, t.full_name, t.username, t.contact, t.address, t.role,
               ('Grade ' || c.grade || ' ' || c.medium::TEXT || ' ' || c.gender_type::TEXT) AS assigned_class
        FROM teachers t
        LEFT JOIN classes c ON c.teacher_id = t.id AND c.academic_year_id = $2
        WHERE t.id = $1
        """,
        user["id"], year_id,
    ))
    task_keys.append("user_profile")

    # Task: Academic Year Details
    tasks.append(db.fetchrow("SELECT * FROM academic_years WHERE id = $1", year_id))
    task_keys.append("academic_year")

    # Dashboard Summary Caches
    cached_students = cache_get(TOTAL_STUDENTS)
    cached_teachers = cache_get(TOTAL_TEACHERS)
    cached_classes = cache_get(TOTAL_CLASSES)
    cached_year = cache_get(CURRENT_YEAR)
    cached_alumnis = cache_get(TOTAL_ALUMNIS)

    if cached_classes is None:
        tasks.append(db.fetchval("SELECT COUNT(*) FROM classes WHERE academic_year_id = $1", year_id))
        task_keys.append("classes")
    if cached_students is None:
        tasks.append(db.fetchval("SELECT COUNT(*) FROM students WHERE status = 'Active'"))
        task_keys.append("students")
    if cached_teachers is None:
        tasks.append(db.fetchval("SELECT COUNT(*) FROM teachers WHERE status = 'Active'"))
        task_keys.append("teachers")
    if cached_year is None:
        tasks.append(db.fetchval("SELECT year_label FROM academic_years WHERE id = $1", year_id))
        task_keys.append("year")
    if cached_alumnis is None:
        tasks.append(db.fetchval("SELECT COUNT(*) FROM students WHERE status = 'Alumni'"))
        task_keys.append("alumnis")

    # Task: Attendance Summary Per-Class Data
    tasks.append(db.fetch(
        """SELECT c.id AS class_id, c.grade, c.medium, c.gender_type,
                  COALESCE(SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END), 0) AS present,
                  COALESCE(SUM(CASE WHEN a.status = 'Absent' THEN 1 ELSE 0 END), 0) AS absent,
                  COUNT(a.id) AS total
           FROM classes c
           LEFT JOIN (
               SELECT att.class_id, att.status, att.id 
               FROM attendance att
               JOIN students st ON att.student_id = st.id
               WHERE att.attendance_date = $1 AND st.current_class_id = att.class_id
           ) a ON a.class_id = c.id
           WHERE c.academic_year_id = $2
           GROUP BY c.id, c.grade, c.medium, c.gender_type
           ORDER BY c.medium, c.grade, c.gender_type""",
        parsed_date, year_id,
    ))
    task_keys.append("class_att_rows")

    # 2. Execute all queries concurrently
    results = await asyncio.gather(*tasks)
    result_map = dict(zip(task_keys, results))

    # 3. Assemble User Profile
    user_row = result_map["user_profile"]
    user_profile = UserProfile(
        id=str(user_row["id"]),
        full_name=user_row["full_name"],
        username=user_row["username"],
        contact=user_row["contact"],
        address=user_row["address"],
        role=user_row["role"],
        assigned_class=user_row["assigned_class"],
    )

    # 4. Assemble Academic Year
    year_row = result_map["academic_year"]
    academic_year = AcademicYearResponse(
        id=str(year_row["id"]),
        year_label=year_row["year_label"],
        start_date=year_row["start_date"],
        end_date=year_row["end_date"],
        is_current=year_row["is_current"],
        created_at=year_row["created_at"],
    )

    # 5. Assemble Attendance Summary
    if cached_classes is not None:
        total_classes = cached_classes
    else:
        total_classes = result_map["classes"]
        cache_set(TOTAL_CLASSES, total_classes)

    if cached_students is not None:
        total_students = cached_students
    else:
        total_students = result_map["students"]
        cache_set(TOTAL_STUDENTS, total_students)

    if cached_teachers is not None:
        total_teachers = cached_teachers
    else:
        total_teachers = result_map["teachers"]
        cache_set(TOTAL_TEACHERS, total_teachers)

    if cached_year is not None:
        current_year = cached_year
    else:
        current_year = result_map["year"] or ""
        cache_set(CURRENT_YEAR, current_year)
        
    if cached_alumnis is not None:
        total_alumnis = cached_alumnis
    else:
        total_alumnis = result_map["alumnis"]
        cache_set(TOTAL_ALUMNIS, total_alumnis)

    class_att_rows = result_map["class_att_rows"]

    present = 0
    absent = 0
    classes_submitted = 0
    classes_data = []
    for r in class_att_rows:
        class_name = f"Grade {r['grade']} {r['medium']} {r['gender_type']}"
        c_present, c_absent, c_total = r["present"], r["absent"], r["total"]
        c_pct = round((c_present / c_total) * 100, 1) if c_total > 0 else 0.0
        present += c_present
        absent += c_absent
        if c_total > 0:
            classes_submitted += 1
        classes_data.append({
            "class_id": str(r["class_id"]),
            "class_name": class_name,
            "present": c_present,
            "absent": c_absent,
            "percentage": c_pct,
            "submitted": c_total > 0,
        })

    total_att = present + absent
    pct = round((present / total_att) * 100, 1) if total_att > 0 else 0.0

    summary = AttendanceSummary(
        total_students=total_students, total_teachers=total_teachers,
        total_classes=total_classes, current_academic_year=current_year,
        total_alumnis=total_alumnis,
        total_present=present, total_absent=absent,
        overall_percentage=pct, date=attendance_date,
        classes_submitted=classes_submitted, classes_total=total_classes,
        classes=classes_data,
    )

    # 6. Return Combined Payload
    return {
        "user": user_profile,
        "academic_year": academic_year,
        "summary": summary,
    }
