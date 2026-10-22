import hashlib, secrets, uuid
from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from config import auth_settings

ph = PasswordHasher()

# hash a secret
def hash_secret(secret: str) -> str:
    return hashlib.sha256(secret.encode()).hexdigest()

# generate a random verification code for pending owners
def generate_verification_code() -> str:
    return secrets.token_urlsafe(16)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return ph.verify(hashed, plain)
    except (VerificationError, InvalidHashError):
        return False
    
def create_access_token(owner_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": owner_id,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=auth_settings.access_token_minutes),
    }
    return jwt.encode(payload, auth_settings.secret_key, algorithm=auth_settings.algorithm)

def decode_token(token: str, expected_type: str) -> dict:
    payload = jwt.decode(
        token,
        auth_settings.secret_key,
        algorithms=[auth_settings.algorithm],                      # pinned, never read from the token
        options={"require": ["exp", "sub", "type"]},
    )
    if payload["type"] != expected_type:
        raise jwt.InvalidTokenError("wrong token type")
    return payload



def new_refresh_token(owner_id: str, jti: str) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": owner_id,
        "type": "refresh",
        "jti": jti,
        "iat": now,
        "exp": now + timedelta(
            days=auth_settings.refresh_token_days
        ),
    }

    return jwt.encode(payload, auth_settings.secret_key, algorithm=auth_settings.algorithm)