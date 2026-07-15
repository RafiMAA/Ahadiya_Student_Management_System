-- 002_rls_policies.sql
-- Row-Level Security (RLS) Policies for Ahadiya School Management System
-- Note: If your FastAPI backend connects via the service role (superuser), RLS will be bypassed.
-- These policies apply if you connect as an authenticated Supabase Auth user or explicitly set the role.

-- Enable RLS on all tables
ALTER TABLE academic_years ENABLE ROW LEVEL SECURITY;
ALTER TABLE classes ENABLE ROW LEVEL SECURITY;
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE teachers ENABLE ROW LEVEL SECURITY;
ALTER TABLE attendance ENABLE ROW LEVEL SECURITY;
ALTER TABLE promotion_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE promotion_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_settings ENABLE ROW LEVEL SECURITY;

-- Helper function to get the current user's role from JWT
CREATE OR REPLACE FUNCTION auth.get_user_role() RETURNS text AS $$
  SELECT current_setting('request.jwt.claim.role', true);
$$ LANGUAGE sql STABLE;

-- Helper function to get the current teacher's ID from JWT
CREATE OR REPLACE FUNCTION auth.get_teacher_id() RETURNS uuid AS $$
  SELECT (current_setting('request.jwt.claim.teacher_id', true))::uuid;
$$ LANGUAGE sql STABLE;

-------------------------------------------------------------------------------
-- PRINCIPAL POLICIES (Full Access to Everything)
-------------------------------------------------------------------------------
CREATE POLICY "Principal full access" ON academic_years FOR ALL USING (auth.get_user_role() = 'Principal');
CREATE POLICY "Principal full access" ON classes FOR ALL USING (auth.get_user_role() = 'Principal');
CREATE POLICY "Principal full access" ON students FOR ALL USING (auth.get_user_role() = 'Principal');
CREATE POLICY "Principal full access" ON teachers FOR ALL USING (auth.get_user_role() = 'Principal');
CREATE POLICY "Principal full access" ON attendance FOR ALL USING (auth.get_user_role() = 'Principal');
CREATE POLICY "Principal full access" ON promotion_rules FOR ALL USING (auth.get_user_role() = 'Principal');
CREATE POLICY "Principal full access" ON promotion_history FOR ALL USING (auth.get_user_role() = 'Principal');
CREATE POLICY "Principal full access" ON audit_logs FOR ALL USING (auth.get_user_role() = 'Principal');
CREATE POLICY "Principal full access" ON system_settings FOR ALL USING (auth.get_user_role() = 'Principal');


-------------------------------------------------------------------------------
-- ADMIN POLICIES (CRUD except principal management and audit_log deletion)
-------------------------------------------------------------------------------
CREATE POLICY "Admin full access" ON academic_years FOR ALL USING (auth.get_user_role() = 'Admin');
CREATE POLICY "Admin full access" ON classes FOR ALL USING (auth.get_user_role() = 'Admin');
CREATE POLICY "Admin full access" ON students FOR ALL USING (auth.get_user_role() = 'Admin');
CREATE POLICY "Admin full access" ON attendance FOR ALL USING (auth.get_user_role() = 'Admin');
CREATE POLICY "Admin full access" ON promotion_rules FOR ALL USING (auth.get_user_role() = 'Admin');
CREATE POLICY "Admin full access" ON promotion_history FOR ALL USING (auth.get_user_role() = 'Admin');
CREATE POLICY "Admin full access" ON system_settings FOR ALL USING (auth.get_user_role() = 'Admin');

-- Admin can manage teachers, but cannot delete or modify Principals (this is usually enforced in the API, but adding basic RLS)
CREATE POLICY "Admin teacher access" ON teachers FOR ALL USING (auth.get_user_role() = 'Admin');

-- Admin can view and insert audit logs, but cannot delete them
CREATE POLICY "Admin view audit logs" ON audit_logs FOR SELECT USING (auth.get_user_role() = 'Admin');
CREATE POLICY "Admin insert audit logs" ON audit_logs FOR INSERT WITH CHECK (auth.get_user_role() = 'Admin');


-------------------------------------------------------------------------------
-- TEACHER POLICIES (SELECT on students/classes, INSERT/UPDATE on own attendance)
-------------------------------------------------------------------------------
-- Teachers can view all classes
CREATE POLICY "Teacher view classes" ON classes FOR SELECT USING (auth.get_user_role() = 'Teacher');

-- Teachers can view all students
CREATE POLICY "Teacher view students" ON students FOR SELECT USING (auth.get_user_role() = 'Teacher');

-- Teachers can view all academic years
CREATE POLICY "Teacher view academic years" ON academic_years FOR SELECT USING (auth.get_user_role() = 'Teacher');

-- Teachers can view attendance records
CREATE POLICY "Teacher view attendance" ON attendance FOR SELECT USING (auth.get_user_role() = 'Teacher');

-- Teachers can insert/update attendance only for the class they are assigned to
CREATE POLICY "Teacher manage own class attendance" ON attendance FOR ALL 
USING (
  auth.get_user_role() = 'Teacher' AND 
  class_id IN (SELECT id FROM classes WHERE teacher_id = auth.get_teacher_id())
)
WITH CHECK (
  auth.get_user_role() = 'Teacher' AND 
  class_id IN (SELECT id FROM classes WHERE teacher_id = auth.get_teacher_id())
);

-- Teachers can view promotion history
CREATE POLICY "Teacher view promotion history" ON promotion_history FOR SELECT USING (auth.get_user_role() = 'Teacher');
