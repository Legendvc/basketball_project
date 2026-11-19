from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from models import Training


def get_training_by_date(
    session: Session,
    training_date: str,
    user_id: int,
) -> list[Training]:
    statement = (
        select(Training)
        .where(
            Training.date == training_date,
             Training.user_id == user_id,
        )
        .order_by(Training.id)
    )

    return list(session.scalars(statement).all())

def create_training(
    session: Session,
    training_date: str,
    shots: int,
    made: int,
    user_id: int,
) -> Training:
    training = Training(
        date=training_date,
        shots=shots,
        made=made,
        user_id=user_id,
    )

    session.add(training)
    session.flush()

    return training

def get_trainings_by_user(
    session: Session,
    user_id: int,
) -> list[Training]:
    statement = (
        select(Training)
        .where(Training.user_id == user_id)
        .order_by(Training.id)
    )

    return list(session.scalars(statement).all())


def update_training(
    session: Session,
    training_id: int,
    user_id: int,
    training_date: str,
    shots: int,
    made: int,
) -> Training | None:
    statement = (
        update(Training)
        .where(Training.id == training_id, Training.user_id == user_id)
        .values(date=training_date, shots=shots, made=made)
        .returning(Training)
    )
    return session.scalars(statement).one_or_none()


def delete_training(session: Session, training_id: int, user_id: int) -> bool:
    statement = (
        delete(Training)
        .where(Training.id == training_id, Training.user_id == user_id)
        .returning(Training.id)
    )
    return session.scalar(statement) is not None
