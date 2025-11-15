# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.services import faculty_service
from app.models.faculty import FacultyOut
from datetime import timedelta

# Import the functions from our new security file
from app.security import create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    This is the main login endpoint.
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

# Endpoint to get info about the logged-in user
# It now correctly depends on get_current_user from security.py
@router.get("/me", response_model=FacultyOut)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """
    A protected endpoint that returns the details
    of the currently logged-in faculty.
    """
    faculty = await faculty_service.get_faculty_by_id(current_user["id"])
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    return faculty