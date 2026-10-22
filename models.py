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
    
    auth_sessions = relationship("AuthSession", back_populates="owner", cascade="all, delete-orphan")
    
class PendingOwner(Base):
    __tablename__ = "pending_owners"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(TEXT, index=True, nullable=False)
    email = Column(TEXT, unique=True, index=True, nullable=False)
    password_hash = Column(TEXT, nullable=False)
    hashed_verification_code = Column(TEXT, nullable=False)
    phone = Column(TEXT)
    expires_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at = Column(DateTime (timezone=True), nullable=False, server_default=func.now())
    
class AuthSession(Base):
    __tablename__ = "auth_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("owners.id"), nullable=False)
    session_label = Column(TEXT, nullable=False)
    last_used_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    revoke_reason = Column(TEXT, nullable=True)

    owner = relationship("Owner", back_populates="auth_sessions")
    refresh_tokens = relationship("RefreshToken", back_populates="session", cascade="all, delete-orphan")
    
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("auth_sessions.id"), nullable=False)
    jti = Column(TEXT, unique=True, nullable=False)
    token_hash = Column(TEXT, unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    used_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    revoke_reason = Column(TEXT, nullable=True)
    replaced_by_id = Column(UUID(as_uuid=True), ForeignKey("refresh_tokens.id"), nullable=True)
    
    session = relationship("AuthSession", back_populates="refresh_tokens")
    self_replacement = relationship("RefreshToken", remote_side=[id], backref="replaced_token")

