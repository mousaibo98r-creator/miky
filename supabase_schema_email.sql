-- Phase 2 Migration: Email Tracking
-- Run this in Supabase SQL Editor to track email outreach
ALTER TABLE mousa
ADD COLUMN IF NOT EXISTS last_contacted_at timestamptz;
