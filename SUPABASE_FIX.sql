-- ==========================================
-- SUPABASE FIX SCRIPT
-- Run this in your Supabase SQL Editor
-- ==========================================

-- 1. Fix "Duplicate Key" errors by ensuring buyer_name is unique
-- This allows the "Upsert" logic in the app to work correctly.
ALTER TABLE mousa ADD CONSTRAINT unique_buyer_name UNIQUE (buyer_name);

-- 2. Fix "Loaded 0 records" and Permission Errors
-- Your app uses the public API key. Access needs to be allowed.

-- Enable RLS (It should be on, but decent to ensure)
ALTER TABLE mousa ENABLE ROW LEVEL SECURITY;

-- Creating a policy involves dropping the old one first to avoid name conflicts.
DROP POLICY IF EXISTS "Enable all access for public" ON mousa;

-- Allow SELECT, INSERT, UPDATE, DELETE for everyone (Public/Anon)
CREATE POLICY "Enable all access for public"
ON mousa
FOR ALL
USING (true)
WITH CHECK (true);

-- 3. Verify
-- After running this, go back to your app.
-- 1. Refresh the page -> Data should load (if any exists).
-- 2. If it's still empty, run `python import_to_db.py` again locally.
