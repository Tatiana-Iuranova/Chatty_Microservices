from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Report  # Импортируй свою модель Report
from datetime import datetime
import psycopg2

DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/admin_db"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

data = [
    {
        "id": 1,
        "post_id": 10,
        "comment_id": None,
        "reporter_id": 5,
        "reason": "Inappropriate language",
        "created_at": "2025-04-23T08:30:15.421Z"
    },
    {
        "id": 2,
        "post_id": None,
        "comment_id": 37,
        "reporter_id": 9,
        "reason": "Spam or misleading",
        "created_at": "2025-04-23T09:15:42.789Z"
    },
    {
        "id": 3,
        "post_id": 7,
        "comment_id": None,
        "reporter_id": 12,
        "reason": "Harassment or bullying",
        "created_at": "2025-04-23T10:45:06.134Z"
    },
    {
        "id": 4,
        "post_id": None,
        "comment_id": 44,
        "reporter_id": 4,
        "reason": "Hate speech",
        "created_at": "2025-04-23T11:20:33.902Z"
    },
    {
        "id": 5,
        "post_id": 3,
        "comment_id": None,
        "reporter_id": 8,
        "reason": "Other",
        "created_at": "2025-04-23T12:55:27.349Z"
    }
]


def insert_data():
    session = SessionLocal()
    try:
        for item in data:
            # Преобразуем строку ISO 8601 в datetime объект
            created_at = datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))

            report = Report(
                id=item["id"],
                post_id=item["post_id"],
                comment_id=item["comment_id"],
                reporter_id=item["reporter_id"],
                reason=item["reason"],
                created_at=created_at
            )
            session.add(report)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error during insert: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    insert_data()