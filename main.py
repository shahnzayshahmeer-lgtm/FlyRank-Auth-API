import os

from fastapi import FastAPI, HTTPException, Depends, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client, Client


# ==================================================
# ENVIRONMENT VARIABLES
# ==================================================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "SUPABASE_URL or SUPABASE_KEY is missing from .env"
    )


# ==================================================
# SUPABASE CLIENT
# ==================================================

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# ==================================================
# FASTAPI APP
# ==================================================

app = FastAPI(
    title="FlyRank Auth API",
    description="Secure Authentication API using FastAPI and Supabase Auth",
    version="1.0"
)


# ==================================================
# SWAGGER BEARER AUTH
# ==================================================

security = HTTPBearer(
    auto_error=False
)


# ==================================================
# STATIC FRONTEND
# ==================================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# ==================================================
# REQUEST MODEL
# ==================================================

class AuthRequest(BaseModel):
    email: str
    password: str


# ==================================================
# REUSABLE AUTH DEPENDENCY
# ==================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Access token required"
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Access token required"
        )

    token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Access token required"
        )

    try:

        response = supabase.auth.get_user(token)

        if response.user is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token"
            )

        return {
            "user": response.user,
            "token": token
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


# ==================================================
# FRONTEND
# ==================================================

@app.get("/", include_in_schema=False)
def home():
    return FileResponse("static/index.html")


# ==================================================
# HEALTH
# ==================================================

@app.get("/health")
def health():

    return {
        "status": "ok",
        "message": "FlyRank Auth API is running"
    }


# ==================================================
# PUBLIC INFO
# ==================================================

@app.get("/public/info")
def public_info():

    return {
        "message": "Welcome stranger! This info is public."
    }


# ==================================================
# SIGN UP
# ==================================================

@app.post("/auth/signup", status_code=201)
def signup(data: AuthRequest):

    email = data.email.strip()
    password = data.password.strip()

    if not email or not password:
        raise HTTPException(
            status_code=400,
            detail="Email and password are required"
        )

    try:

        response = supabase.auth.sign_up(
            {
                "email": email,
                "password": password
            }
        )

        if response.user is None:
            raise HTTPException(
                status_code=400,
                detail="Unable to create user"
            )

        return {
            "message": "User created successfully",
            "user": {
                "id": response.user.id,
                "email": response.user.email
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ==================================================
# LOGIN
# ==================================================

@app.post("/auth/login")
def login(data: AuthRequest):

    email = data.email.strip()
    password = data.password.strip()

    if not email or not password:
        raise HTTPException(
            status_code=400,
            detail="Email and password are required"
        )

    try:

        response = supabase.auth.sign_in_with_password(
            {
                "email": email,
                "password": password
            }
        )

        if response.session is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid login credentials"
            )

        return {
            "message": "Login successful",
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer"
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid login credentials"
        )


# ==================================================
# PROTECTED PROFILE
# ==================================================

@app.get("/protected/profile")
def protected_profile(
    auth_data=Depends(get_current_user)
):

    user = auth_data["user"]

    return {
        "message": "Protected profile accessed successfully",
        "user": {
            "id": user.id,
            "email": user.email,
            "created_at": str(user.created_at)
        }
    }


# ==================================================
# PROTECTED DASHBOARD
# ==================================================

@app.get("/protected/dashboard")
def protected_dashboard(
    auth_data=Depends(get_current_user)
):

    user = auth_data["user"]

    return {
        "message": "Welcome to the protected dashboard",
        "user_email": user.email
    }


# ==================================================
# LOGOUT
# ==================================================

@app.post("/auth/logout", status_code=204)
def logout(
    auth_data=Depends(get_current_user)
):

    try:

        supabase.auth.sign_out()

        return Response(status_code=204)

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Logout failed"
        )