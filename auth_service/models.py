from sqlalchemy import Column, Integer, String, DateTime, Boolean, func
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from datetime import datetime


Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_code: Mapped[str] = mapped_column(String(6), nullable=True)

    # # Связь с постами
    # posts: Mapped[list['Post']] = relationship('Post', back_populates='author')
