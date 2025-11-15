# app/security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

from app.config import settings # Import settings

# This tells FastAPI what "security scheme" we're using.
# tokenUrl="auth/login" points to our login endpoint.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

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

# --- Token Validation Dependency ---
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    This dependency validates the token and returns the user.
    All protected endpoints will use this.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        user_id: str = payload.get("id")
        if email is None or user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    return {"email": email, "id": user_id}
# --------------------------------------