-- ============================================================
-- Student Achievements table
-- Stores per-student achievements across academic years.
-- These records are NEVER deleted during promotion/graduation.
-- ============================================================

CREATE TABLE student_achievements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    academic_year_id UUID NOT NULL REFERENCES academic_years(id) ON DELETE CASCADE,
    grade INT NOT NULL CHECK (grade >= 1 AND grade <= 11),
    achievement_text TEXT NOT NULL,
    created_by UUID NOT NULL REFERENCES teachers(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_achievements_student ON student_achievements (student_id);
CREATE INDEX idx_achievements_year ON student_achievements (academic_year_id);
CREATE INDEX idx_achievements_created_by ON student_achievements (created_by);
