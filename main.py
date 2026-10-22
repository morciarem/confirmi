from datetime import datetime,timezone
import asyncio

from contextlib import asynccontextmanager
from tasks import cleanup_expired_users
from argon2 import PasswordHasher
from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from emailer import send_email
import models, schemas
from database import engine, get_db
from security import generate_verification_code, hash_secret
from config import settings
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from auth import router as auth_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: launch the cleanup task.
    task = asyncio.create_task(cleanup_expired_users())

    yield

    # Shutdown: stop the cleanup task gracefully.
    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(lifespan=lifespan)

# Identify clients by their IP address
limiter = Limiter(key_func=get_remote_address)

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

app.include_router(auth_router)


models.Base.metadata.create_all(bind=engine)

ph = PasswordHasher()

@app.get("/")
async def main():
    return {"message": "Hello, World!"}

# SignUp endpoint for owners
@app.post("/signup", response_model=schemas.OwnerResponse)
@limiter.limit(settings.signup_limit)  # Apply rate limiting to the signup endpoint
async def signup(request: Request, data: schemas.RegisterOwner, db: Session = Depends(get_db)):
    
    # Check if the email already exists
    existing_owner = db.query(models.Owner).filter(models.Owner.email == data.email).first() or db.query(models.PendingOwner).filter(models.PendingOwner.email == data.email).first()
    if existing_owner:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create a verification code for the pending owner
    verification_code = generate_verification_code()
    
    
    # Create a new pending owner
    pending_owner = models.PendingOwner(
        name=data.name,
        email=data.email,
        phone=data.phone,
        password_hash=ph.hash(data.password),
        hashed_verification_code=hash_secret(verification_code)
    )
    db.add(pending_owner)
    db.commit()
    db.refresh(pending_owner)
    
    # Send the verification email
    send_email(to_email=data.email, verification_code=verification_code)
    return {"message": "Please check your email for the verification code."}

# Verify endpoint for owners
@app.post("/verify", response_model=schemas.OwnerResponse)
@limiter.limit(settings.signup_limit)  # Apply rate limiting to the verify endpoint
async def verify(request: Request, data: schemas.VerifyRequest, db: Session = Depends(get_db)):
    # Check if the pending owner exists
    pending_owner = db.query(models.PendingOwner).filter(models.PendingOwner.email == data.email).first()
    if not pending_owner:
        raise HTTPException(status_code=400, detail="Pending owner not found")
    # Check if the verification code is correct and did not expires
    valid_verification_code = pending_owner.hashed_verification_code == hash_secret(data.verification_code) and pending_owner.expires_at > datetime.now(timezone.utc)
    if not valid_verification_code:
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")
    
    # Create a new owner
    owner = models.Owner(
        name=pending_owner.name,
        email=pending_owner.email,
        phone=pending_owner.phone,
        password_hash=pending_owner.password_hash
    )
    db.add(owner)
    db.delete(pending_owner)  # Remove the pending owner after verification
    db.commit()
    db.refresh(owner)
    return {"message": "Owner verified successfully. Please log in."}