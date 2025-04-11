from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Subscription(Base):
    __tablename__ = 'subscriptions'

    user_id: Mapped[int] = mapped_column(primary_key=True)  # ID пользователя, на которого подписываются
    follower_id: Mapped[int] = mapped_column(primary_key=True)  # ID подписчика