-- CivicTrack AI Database Migration
-- This file contains the SQL changes needed for the work assignment feature

-- Add assigned_to and resolved_at columns to issues table
ALTER TABLE issues 
ADD COLUMN assigned_to INT DEFAULT NULL,
ADD COLUMN resolved_at TIMESTAMP DEFAULT NULL,
ADD FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL;

-- Create issue_assignments table for tracking assignments
CREATE TABLE IF NOT EXISTS issue_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    issue_id INT NOT NULL,
    assigned_by INT NOT NULL,
    assigned_to INT NOT NULL,
    assignment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (issue_id) REFERENCES issues(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE CASCADE,
    INDEX (issue_id),
    INDEX (assigned_to)
);

-- Create issue_resolutions table for tracking completed work
CREATE TABLE IF NOT EXISTS issue_resolutions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    issue_id INT NOT NULL,
    resolved_by INT NOT NULL,
    comments TEXT,
    resolution_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (issue_id) REFERENCES issues(id) ON DELETE CASCADE,
    FOREIGN KEY (resolved_by) REFERENCES users(id) ON DELETE CASCADE,
    INDEX (issue_id),
    INDEX (resolved_by)
);

-- Add index on assigned_to for faster queries
CREATE INDEX idx_assigned_to ON issues(assigned_to);
CREATE INDEX idx_status ON issues(status);
