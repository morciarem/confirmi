from argon2 import PasswordHasher
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import engine, get_db

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

ph = PasswordHasher()




@app.get("/")
async def main():
    return {"message": "Hello, World!"}

# Register endpoint for owners
@app.post("/register", response_model=schemas.OwnerResponse)
async def register(data: schemas.RegisterOwner, db: Session = Depends(get_db)):
    owner = models.Owner(
        name=data.name,
        email=data.email,
        phone=data.phone,
        password_hash=ph.hash(data.password)
    )
    print(f"Registering owner: {owner.name}, Email: {owner.email}")
    db.add(owner)
    db.commit()
    db.refresh(owner)
    return owner