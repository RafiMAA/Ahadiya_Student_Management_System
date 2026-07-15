ALTER TABLE attendance ALTER COLUMN marked_by DROP NOT NULL;
ALTER TABLE attendance DROP CONSTRAINT attendance_marked_by_fkey;
ALTER TABLE attendance ADD CONSTRAINT attendance_marked_by_fkey FOREIGN KEY (marked_by) REFERENCES teachers(id) ON DELETE SET NULL;

ALTER TABLE promotion_history ALTER COLUMN promoted_by DROP NOT NULL;
ALTER TABLE promotion_history DROP CONSTRAINT promotion_history_promoted_by_fkey;
ALTER TABLE promotion_history ADD CONSTRAINT promotion_history_promoted_by_fkey FOREIGN KEY (promoted_by) REFERENCES teachers(id) ON DELETE SET NULL;

ALTER TABLE audit_logs ALTER COLUMN performed_by DROP NOT NULL;
ALTER TABLE audit_logs DROP CONSTRAINT audit_logs_performed_by_fkey;
ALTER TABLE audit_logs ADD CONSTRAINT audit_logs_performed_by_fkey FOREIGN KEY (performed_by) REFERENCES teachers(id) ON DELETE SET NULL;

ALTER TABLE system_settings DROP CONSTRAINT IF EXISTS system_settings_updated_by_fkey;
ALTER TABLE system_settings ADD CONSTRAINT system_settings_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES teachers(id) ON DELETE SET NULL;
