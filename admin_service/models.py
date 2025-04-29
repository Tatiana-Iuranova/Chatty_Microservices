from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from typing import Optional
from sqlalchemy import  Text, DateTime
from sqlalchemy import CheckConstraint
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean


Base = declarative_base()

class Report(Base):
    __tablename__ = 'reports'

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[Optional[int]] = mapped_column(nullable=True)         # просто ID-шник
    comment_id: Mapped[Optional[int]] = mapped_column(nullable=True)      # просто ID-шник
    reporter_id: Mapped[Optional[int]] = mapped_column(nullable=True)    # просто ID-шник
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            '(post_id IS NOT NULL AND comment_id IS NULL) OR (post_id IS NULL AND comment_id IS NOT NULL)',
            name='only_one_of_post_or_comment'
        ),
    )


class User(Base):
    __tablename__ = "users"

    # id — это идентификатор пользователя. Типизация через Mapped.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # роль пользователя (по умолчанию 'user')
    role: Mapped[str] = mapped_column(String, default="user")

    # блокировка пользователя (по умолчанию False)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
