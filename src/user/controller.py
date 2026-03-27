from src.user.dtos import UserSchema, LoginSchema
from sqlalchemy.orm import Session
from src.user.models import UserModel
from fastapi import HTTPException, status, Request
from pwdlib import PasswordHash
from src.utils.settings import settings
from datetime import datetime, timedelta, timezone
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
    user = db.query(UserModel).filter(
        UserModel.username == body.username
    ).first()

    # Valid username and password check
    if not user or not verify_password(body.password, user.hash_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    expiry_time = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    token_payload = {
        "_id": user.id,
        "exp": expiry_time.timestamp()
    }

    token = jwt.encode(
        token_payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return {"token": token}


def is_authenticated(request: Request, db: Session):
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token"
        )

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    user_id = payload.get("_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    user = db.query(UserModel).filter(UserModel.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user