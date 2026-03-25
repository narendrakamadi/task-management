from src.user.dtos import UserSchema, LoginSchema
from sqlalchemy.orm import Session
from src.user.models import UserModel
from fastapi import HTTPException, status
from pwdlib import PasswordHash
from src.utils.settings import settings
from datetime import datetime, timedelta
import jwt

password_hash = PasswordHash.recommended()

def get_password_hash(password):
    return password_hash.hash(password)


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def register(body: UserSchema, db: Session):
    # Check if username already exist
    is_user = db.query(UserModel).filter(
        (UserModel.username == body.username) |
        (UserModel.email == body.email)
    ).first()

    if is_user:
        raise HTTPException(
            status_code=400, 
            detail="Username or email already exist."
        )
    
    # Hash Password
    password_hash = get_password_hash(body.password)

    # Create user object
    new_user = UserModel(
        name=body.name,
        username=body.username,
        email=body.email,
        hash_password=password_hash,
        is_active=True
    )

    # Save to DB
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

def login(body: LoginSchema, db: Session):
    user = db.query(UserModel).filter(UserModel.username == body.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You entered wrong username.")
    
    if not verify_password(body.password, user.hash_password):
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You entered wrong password.")
    
    expiry_time = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    token = jwt.encode({"_id":user.id, "exp":expiry_time}, settings.SECRET_KEY, settings.ALGORITHM)

    return {"token": token}