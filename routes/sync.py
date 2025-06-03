from fastapi import APIRouter, Request
from supabase_client import supabase

router = APIRouter()

@router.post("/sync-app-user")
async def sync_app_user(request: Request):
    data = await request.json()
    user_id = data.get("id")
    email = data.get("email")

    if not user_id or not email:
        return {"error": "Missing user_id or email"}, 400

    try:
        supabase.table("app_users").upsert({
            "id": user_id,
            "email": email
        }, on_conflict="id").execute()
        return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}, 500
