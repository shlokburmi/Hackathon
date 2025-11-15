# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.services import faculty_service
from app.config import settings
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

router = APIRouter(prefix="/auth", tags=["Authentication"])

# --- Token Creation ---
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Default token expiry: 30 minutes
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    
    to_encode.update({"exp": expire})
    # Use your SECRET_KEY from .env
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt
# ----------------------


@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    This is the main login endpoint.
    It uses OAuth2PasswordRequestForm, so it expects 'username' and 'password'
    sent in a form-data request.
    """
    
    # 1. Find the user by email (which is the 'username' in the form)
    user = await faculty_service.get_faculty_by_email(form_data.username)
    
    # 2. Check if user exists and password is correct
    if not user or not faculty_service.verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Create a token for them
    access_token_expires = timedelta(minutes=60) # Token valid for 60 minutes
    access_token = create_access_token(
        data={"sub": user["email"], "id": user["_id"]}, 
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}