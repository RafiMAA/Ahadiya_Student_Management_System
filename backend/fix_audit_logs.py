import os
import re

files = [
    "app/routes/teacher_routes.py",
    "app/routes/student_routes.py",
    "app/routes/attendance_routes.py",
    "app/routes/class_routes.py",
    "app/routes/academic_year_routes.py",
    "app/routes/promotion_routes.py",
    "app/routes/import_routes.py",
]

for file in files:
    with open(file, "r") as f:
        content = f.read()

    # Look for: db.execute("INSERT INTO audit_logs (action, details, performed_by) VALUES ($1, $2, $3)", "SOME_ACTION", {...}, user["id"])
    # We replace $2 with $2::jsonb
    content = content.replace("VALUES ($1, $2, $3)", "VALUES ($1, $2::jsonb, $3)")

    # Ensure import json exists
    if "import json" not in content:
        content = "import json\n" + content

    # Use regex to find `db.execute(` calls for audit_logs and wrap the dictionary parameter in json.dumps
    # This is tricky because the dict parameter can span multiple lines.
    # Actually, a simpler way is to just use a custom function for DB logs that does it centrally,
    # but the simplest way without refactoring is to find the exact dictionary definitions.
