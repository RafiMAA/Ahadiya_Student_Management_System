-- ============================================================
-- Ahadiya School Management System — Database Schema
-- Run this FIRST in your Supabase SQL Editor
-- ============================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- ENUM TYPES
-- ============================================================

CREATE TYPE medium_type AS ENUM ('Sinhala', 'Tamil');
CREATE TYPE gender_type_enum AS ENUM ('Mixed', 'Boys', 'Girls');
CREATE TYPE gender_enum AS ENUM ('Male', 'Female');
CREATE TYPE student_status AS ENUM ('Active', 'Alumni', 'Inactive');
CREATE TYPE teacher_role AS ENUM ('Principal', 'Admin', 'Teacher');
CREATE TYPE teacher_status AS ENUM ('Active', 'Inactive');
CREATE TYPE attendance_status AS ENUM ('Present', 'Absent');

-- ============================================================
-- TABLE: academic_years
-- ============================================================

CREATE TABLE academic_years (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    year_label VARCHAR(10) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_academic_years_current ON academic_years (is_current) WHERE is_current = TRUE;

-- ============================================================
-- TABLE: teachers
-- ============================================================

CREATE TABLE teachers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name VARCHAR(255) NOT NULL,
    contact VARCHAR(20) NOT NULL,
    address TEXT,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role teacher_role DEFAULT 'Teacher',
    status teacher_status DEFAULT 'Active',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_teachers_username ON teachers (username);
CREATE INDEX idx_teachers_status ON teachers (status);

-- ============================================================
-- TABLE: classes
-- ============================================================

CREATE TABLE classes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    grade INT NOT NULL CHECK (grade >= 1 AND grade <= 11),
    medium medium_type NOT NULL,
    gender_type gender_type_enum NOT NULL,
    academic_year_id UUID NOT NULL REFERENCES academic_years(id) ON DELETE CASCADE,
    teacher_id UUID REFERENCES teachers(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (grade, medium, gender_type, academic_year_id)
);

CREATE INDEX idx_classes_academic_year ON classes (academic_year_id);
CREATE INDEX idx_classes_teacher ON classes (teacher_id);
CREATE INDEX idx_classes_grade_medium ON classes (grade, medium);

-- ============================================================
-- TABLE: students
-- ============================================================

CREATE TABLE students (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    registration_number VARCHAR(20) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    gender gender_enum NOT NULL,
    date_of_birth DATE NOT NULL,
    parent_name VARCHAR(255) NOT NULL,
    parent_contact VARCHAR(20) NOT NULL,
    medium medium_type NOT NULL,
    current_grade INT NOT NULL CHECK (current_grade >= 1 AND current_grade <= 11),
    current_class_id UUID REFERENCES classes(id) ON DELETE SET NULL,
    status student_status DEFAULT 'Active',
    joined_date DATE NOT NULL,
    graduation_year VARCHAR(10),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_students_class ON students (current_class_id);
CREATE INDEX idx_students_status ON students (status);
CREATE INDEX idx_students_grade ON students (current_grade);
CREATE INDEX idx_students_medium ON students (medium);
CREATE INDEX idx_students_registration ON students (registration_number);

-- ============================================================
-- TABLE: attendance
-- ============================================================

CREATE TABLE attendance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    class_id UUID NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    attendance_date DATE NOT NULL,
    status attendance_status NOT NULL,
    marked_by UUID REFERENCES teachers(id) ON DELETE SET NULL,
    is_locked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (student_id, attendance_date)
);

CREATE INDEX idx_attendance_class_date ON attendance (class_id, attendance_date);
CREATE INDEX idx_attendance_student ON attendance (student_id);
CREATE INDEX idx_attendance_date ON attendance (attendance_date);

-- ============================================================
-- TABLE: promotion_rules
-- ============================================================

CREATE TABLE promotion_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_class_id UUID NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    male_to_class_id UUID REFERENCES classes(id) ON DELETE SET NULL,
    female_to_class_id UUID REFERENCES classes(id) ON DELETE SET NULL,
    academic_year_id UUID NOT NULL REFERENCES academic_years(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_promotion_rules_year ON promotion_rules (academic_year_id);
CREATE INDEX idx_promotion_rules_from ON promotion_rules (from_class_id);

-- ============================================================
-- TABLE: promotion_history
-- ============================================================

CREATE TABLE promotion_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    from_class_id UUID NOT NULL REFERENCES classes(id),
    to_class_id UUID NOT NULL REFERENCES classes(id),
    academic_year_id UUID NOT NULL REFERENCES academic_years(id),
    promoted_at TIMESTAMPTZ DEFAULT NOW(),
    promoted_by UUID REFERENCES teachers(id) ON DELETE SET NULL
);

CREATE INDEX idx_promotion_history_student ON promotion_history (student_id);
CREATE INDEX idx_promotion_history_year ON promotion_history (academic_year_id);

-- ============================================================
-- TABLE: audit_logs
-- ============================================================

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    action VARCHAR(100) NOT NULL,
    details JSONB DEFAULT '{}',
    performed_by UUID REFERENCES teachers(id) ON DELETE SET NULL,
    performed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_action ON audit_logs (action);
CREATE INDEX idx_audit_logs_performed_by ON audit_logs (performed_by);
CREATE INDEX idx_audit_logs_performed_at ON audit_logs (performed_at DESC);

-- ============================================================
-- TABLE: system_settings
-- ============================================================

CREATE TABLE system_settings (
    key VARCHAR(100) PRIMARY KEY,
    value VARCHAR(500) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_by UUID REFERENCES teachers(id) ON DELETE SET NULL
);

-- ============================================================
-- HELPER FUNCTION: Generate class display name
-- ============================================================

CREATE OR REPLACE FUNCTION get_class_name(p_grade INT, p_medium medium_type, p_gender_type gender_type_enum)
RETURNS TEXT AS $$
BEGIN
    RETURN 'Grade ' || p_grade || ' ' || p_medium::TEXT || ' ' || p_gender_type::TEXT;
END;
$$ LANGUAGE plpgsql IMMUTABLE;
