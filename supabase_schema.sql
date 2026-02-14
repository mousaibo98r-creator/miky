-- Run this in your Supabase SQL Editor to update the 'mousa' table
ALTER TABLE mousa
ADD COLUMN IF NOT EXISTS email text,
ADD COLUMN IF NOT EXISTS phone text,
ADD COLUMN IF NOT EXISTS website text,
ADD COLUMN IF NOT EXISTS address text,
ADD COLUMN IF NOT EXISTS last_scavenged_at timestamptz;
