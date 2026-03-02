USE civictrack_ai;

-- Add verification_status column if it doesn't exist
ALTER TABLE issues ADD COLUMN IF NOT EXISTS verification_status VARCHAR(50) DEFAULT 'Pending';

-- Add verified_by column if it doesn't exist  
ALTER TABLE issues ADD COLUMN IF NOT EXISTS verified_by INT DEFAULT NULL;

-- Add image_path to issue_resolutions if it doesn't exist
ALTER TABLE issue_resolutions ADD COLUMN IF NOT EXISTS image_path VARCHAR(255);

-- Add foreign key constraint if it doesn't exist
ALTER TABLE issues ADD CONSTRAINT fk_verified_by FOREIGN KEY (verified_by) REFERENCES users(id) ON DELETE SET NULL;

-- Add indexes
ALTER TABLE issues ADD INDEX IF NOT EXISTS idx_verification_status (verification_status);
ALTER TABLE issues ADD INDEX IF NOT EXISTS idx_verified_by (verified_by);

-- Verify the migration
SELECT "Verification migration completed!" AS status;
