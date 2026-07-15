-- ============================================================
-- Ahadiya School Management System — Database Schema Optimization
-- Adds Trigram Indexes for fast text searching on students
-- ============================================================

-- Enable the pg_trgm extension if not already enabled
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create GIN index for full_name
CREATE INDEX IF NOT EXISTS idx_students_search_name 
ON students USING gin (full_name gin_trgm_ops);

-- Create GIN index for registration_number
CREATE INDEX IF NOT EXISTS idx_students_search_reg 
ON students USING gin (registration_number gin_trgm_ops);
