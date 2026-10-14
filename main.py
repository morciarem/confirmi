from time import timezone

from argon2 import PasswordHasher
from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from emailer import send_email
import models, schemas
from database import engine, get_db
from security import generate_verification_code, hash_secret
from config import settings

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

ph = PasswordHasher()




@app.get("/")
async def main():
    return {"message": "Hello, World!"}

# SignUp endpoint for owners
@app.post("/signup", response_model=schemas.OwnerResponse)
async def signup(data: schemas.RegisterOwner, db: Session = Depends(get_db)):
    
    # Check if the email already exists
    existing_owner = db.query(models.Owner).filter(models.Owner.email == data.email).first()
    if existing_owner:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create a verification code for the pending owner
    verification_code = generate_verification_code()
    
    # Create a verification URL
    verification_url = f"{settings.frontend_url}/verify?email={data.email}&code={verification_code}"
    
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
    send_email(to_email=data.email, link=verification_url)
    return pending_owner

# Verify endpoint for owners
@app.get("/verify", response_model=schemas.OwnerResponse)
async def verify(request: Request, db: Session = Depends(get_db)):
    params = request.query_params
    # Check if the pending owner exists
    pending_owner = db.query(models.PendingOwner).filter(models.PendingOwner.email == params.get("email")).first()
    if not pending_owner:
        raise HTTPException(status_code=400, detail="Pending owner not found")
    # Check if the verification code is correct
    if pending_owner.hashed_verification_code != hash_secret(params.get("code")):
        raise HTTPException(status_code=400, detail="Invalid verification code")
    
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
    return owner