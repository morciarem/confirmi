
from datetime import datetime, timedelta, timezone
import uuid
import jwt

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

import models
from database import get_db
from security import (
    create_access_token,
    new_refresh_token,
    decode_token,
    hash_secret,
)
from security import verify_password
import schemas
from utilities import add_to_db

router = APIRouter(prefix="/auth", tags=["Authentication"])
limiter = Limiter(key_func=get_remote_address)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/login")
@limiter.limit("5/minute")
def login(
    request: Request,
    email: str,
    password: str,
    db: Session = Depends(get_db),
):
    owner = (
        db.query(models.Owner)
        .filter(models.Owner.email == email)
        .first()
    )

    if not owner or not verify_password(
        password, owner.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    

    # Create a session for the owner
    auth_session = models.AuthSession(
        owner_id=owner.id,
        session_label="Default Session",
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )

    try:
        # Add the session to the transaction
        db.add(auth_session)
        
        # Write pending inserts so auth_session.id is available
        db.flush()
        

        # Generate the refresh token
        jti = uuid.uuid4()
        token = new_refresh_token(str(owner.id), str(jti))

        # Create the refresh token record
        refresh_token = models.RefreshToken(
            session_id=auth_session.id,
            jti=jti,
            token_hash=hash_secret(token),
        )

        db.add(refresh_token)


        # Commit both inserts together
        db.commit()

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Login Failed. Please try again later.",
        )

    
    


    return {
        "access_token": create_access_token(str(owner.id)),
        "refresh_token": token,
        "token_type": "bearer",
    }


@router.post("/refresh")
@limiter.limit("5/minute")
def refresh_tokens(request: Request, token: str):
    try:
        payload = decode_token(
            token,
            expected_type="refresh",
        )
    except (jwt.InvalidTokenError, TypeError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token",
        )

    owner_id = payload["sub"]

    # In production, verify the refresh token is still
    # active in your database before issuing new tokens.

    return {
        "access_token": create_access_token(owner_id),
        "refresh_token": new_refresh_token(owner_id, payload["jti"]),
        "token_type": "bearer",
    }


def get_current_owner(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    try:
        payload = decode_token(token, expected_type="access")
        owner_id = payload["sub"]
    except (jwt.InvalidTokenError, TypeError, ValueError, KeyError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    owner = db.get(models.Owner, owner_id)

    if owner is None:
        raise HTTPException(status_code=401, detail="Owner not found")

    return owner
