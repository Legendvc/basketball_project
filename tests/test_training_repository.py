from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Base, Training, User
from training_repository import get_training_by_date


def test_get_training_by_date_filters_user_and_date():
    engine = create_engine("sqlite:///:memory:")

    try:
        Base.metadata.create_all(engine)

        with Session(engine) as session:
            richard = User(username="Richard")
            alice = User(username="Alice")

            richard_today = Training(
                user=richard,
                date="2026-10-15",
                shots=10,
                made=8,
            )
            alice_today = Training(
                user=alice,
                date="2026-10-15",
                shots=20,
                made=12,
            )
            richard_next_day = Training(
                user=richard,
                date="2026-10-16",
                shots=5,
                made=3,
            )

            session.add_all([
                richard_today,
                alice_today,
                richard_next_day,
            ])
            session.commit()

            records = get_training_by_date(
                session,
                "2026-10-15",
                user_id=richard.id,
            )

            assert [record.id for record in records] == [
                richard_today.id
            ]

            empty_records = get_training_by_date(
                session,
                "2099-01-01",
                user_id=richard.id,
            )

            assert empty_records == []
    finally:
        engine.dispose()