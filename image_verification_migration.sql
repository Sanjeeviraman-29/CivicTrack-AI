-- CivicTrack AI - Image Verification Feature Database Migration
-- Run this SQL script manually using MySQL Workbench or mysql command line
-- Command: mysql -u root -p civictrack_ai < image_verification_migration.sql

USE civictrack_ai;

-- 1. Add verification columns to issues table
ALTER TABLE issues ADD COLUMN IF NOT EXISTS verification_status VARCHAR(50) DEFAULT 'Pending' AFTER resolved_at;
ALTER TABLE issues ADD COLUMN IF NOT EXISTS verified_by INT AFTER verification_status;

-- 2. Add image storage to issue_resolutions table
ALTER TABLE issue_resolutions ADD COLUMN IF NOT EXISTS image_path VARCHAR(255) AFTER comments;
ALTER TABLE issue_resolutions ADD COLUMN IF NOT EXISTS verification_date TIMESTAMP AFTER image_path;

-- 3. Create verification_history table for audit trail
CREATE TABLE IF NOT EXISTS verification_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    issue_id INT NOT NULL,
    verified_by INT NOT NULL,
    action VARCHAR(20) NOT NULL COMMENT 'Approved or Rejected',
    reason VARCHAR(255),
    verification_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (issue_id) REFERENCES issues(id),
    FOREIGN KEY (verified_by) REFERENCES users(id),
    INDEX idx_issue (issue_id),
    INDEX idx_verified_by (verified_by)
);

-- 4. Update status values explanation
-- Status values for issues.status: 'Pending', 'In Progress', 'Awaiting Verification', 'Resolved'
-- Verification status values: 'Pending', 'Verified', 'Rejected'

-- 5. Add indexes for performance
ALTER TABLE issues ADD INDEX IF NOT EXISTS idx_verification_status (verification_status);
ALTER TABLE issues ADD INDEX IF NOT EXISTS idx_verified_by (verified_by);

-- 6. Verify schema was created correctly
DESCRIBE issues;
DESCRIBE issue_resolutions;
DESCRIBE verification_history;

-- All done!
SELECT "✓ Image Verification schema migration completed!" AS status;
