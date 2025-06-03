# supabase_client.py
# This file initializes the Supabase client for use in the application.
# It uses environment variables to securely access the Supabase URL and key.
from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # ← change this


supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

