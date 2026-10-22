
import jwt

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

import models
from database import get_db
from security import (
    create_access_token,
    new_refresh_token,
    decode_token,
)
from security import verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/login")
def login(
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

    owner_id = str(owner.id)

    return {
        "access_token": create_access_token(owner_id),
        "refresh_token": new_refresh_token(owner_id),
        "token_type": "bearer",
    }


@router.post("/refresh")
def refresh_tokens(token: str):
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
        "refresh_token": new_refresh_token(owner_id),
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
