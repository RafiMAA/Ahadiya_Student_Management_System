-- ============================================================
-- Performance Indexes
-- ============================================================

-- Composite index for teacher -> class lookup used in auth and teacher routes
-- This speeds up the correlated subqueries in dashboard_routes.py and others
CREATE INDEX IF NOT EXISTS idx_classes_teacher_year ON classes (teacher_id, academic_year_id);
