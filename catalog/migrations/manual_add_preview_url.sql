-- Add preview_url column to carti_catalog table
ALTER TABLE carti_catalog ADD COLUMN IF NOT EXISTS preview_url VARCHAR(255);