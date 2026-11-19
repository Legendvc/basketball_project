from sqlalchemy.orm import Session

from training_repository import get_trainings_by_user
from training_summary import TrainingSummary


def get_training_summary(
    session: Session,
    user_id: int,
    limit: int = 5,
) -> dict:
    records = get_trainings_by_user(session, user_id=user_id)

    history = [
        {
            "date": record.date,
            "shots": record.shots,
            "made": record.made,
        }
        for record in records
    ]

    return TrainingSummary(
        history
    ).get_recent_effective_training_days_summary(limit=limit)