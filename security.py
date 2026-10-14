import hashlib, secrets, uuid
from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

#from config import settings

ph = PasswordHasher()
DUMMY_HASH = ph.hash("dummy-password-for-timing")  # see /login
ALGORITHM = "HS256"

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
    
# def create_access_token(owner_id: uuid.UUID) -> str:
#     now = datetime.now(timezone.utc)
#     payload = {
#         "sub": str(owner_id),
#         "type": "access",
#         "iat": now,
#         "exp": now + timedelta(minutes=settings.access_token_minutes),
#     }
#     return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)

# def decode_access_token(token: str) -> dict:
#     payload = jwt.decode(
#         token,
#         settings.secret_key,
#         algorithms=[ALGORITHM],                      # pinned, never read from the token
#         options={"require": ["exp", "sub", "type"]},
#     )
#     if payload["type"] != "access":
#         raise jwt.InvalidTokenError("wrong token type")
#     return payload


# def hash_refresh_token(raw: str) -> str:
#     return hashlib.sha256(raw.encode()).hexdigest()


# def new_refresh_token() -> tuple[str, str]:
#     raw = secrets.token_urlsafe(48)
#     return raw, hash_refresh_token(raw)