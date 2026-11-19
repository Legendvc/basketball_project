import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from models import Base, Training, User
from training_repository import create_training


@pytest.mark.parametrize(
    "should_commit, expected_count",
    [
        (True, 1),
        (False, 0),
    ],
)
def test_create_training_respects_transaction(
    should_commit,
    expected_count,
):
    engine = create_engine("sqlite:///:memory:")

    try:
        Base.metadata.create_all(engine)

        with Session(engine) as session:
            session.add(User(id=1, username="Richard"))
            session.commit()

            training = create_training(
                session=session,
                training_date="2026-11-14",
                shots=10,
                made=8,
                user_id=1,
            )

            assert training.id is not None

            if should_commit:
                session.commit()
            else:
                session.rollback()

        with Session(engine) as session:
            count = session.scalar(
                select(func.count()).select_from(Training)
            )

            assert count == expected_count
    finally:
        engine.dispose()