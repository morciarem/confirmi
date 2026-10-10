import uuid
from sqlalchemy import TEXT, UUID, Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database import Base

class Owner(Base):
    __tablename__ = "owners"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(TEXT, index=True, nullable=False)
    email = Column(TEXT, unique=True, index=True, nullable=False)
    password_hash = Column(TEXT, nullable=False)
    phone = Column(TEXT)
    created_at = Column(DateTime (timezone=True), nullable=False, server_default=func.now())
