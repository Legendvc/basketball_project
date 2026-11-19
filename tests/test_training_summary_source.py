from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Base, Training, User
from training_repository import get_trainings_by_user


def test_database_records_preserve_summary_rules(player):
    engine = create_engine("sqlite:///:memory:")

    try:
        Base.metadata.create_all(engine)

        with Session(engine) as session:
            session.add_all([
                User(id=1, username="Richard"),
                User(id=2, username="Alice"),
            ])
            session.flush()

            session.add_all([
                Training(
                    user_id=1, date="2026-11-02", shots=3, made=2,
                ),
                Training(
                    user_id=1, date="2026-11-02", shots=2, made=1,
                ),
                Training(
                    user_id=1, date="2026-11-01", shots=10, made=9,
                ),
                Training(
                    user_id=1, date="2026-11-03", shots=4, made=4,
                ),
                Training(
                    user_id=2, date="2026-11-02", shots=20, made=20,
                ),
            ])
            session.commit()

            records = get_trainings_by_user(session, user_id=1)

            # 用现有 Player 统计方法作为重构前的基准。
            player.training_history = [
                {
                    "date": record.date,
                    "shots": record.shots,
                    "made": record.made,
                }
                for record in records
            ]

            summary = player.get_recent_effective_training_days_summary(
                limit=2
            )

            assert summary["training_days"] == 2
            assert summary["shots"] == 15
            assert summary["made"] == 12
            assert summary["percentage"] == 80.0
            assert summary["is_reference_only"] is False
            assert [day["date"] for day in summary["days"]] == [
                "2026-11-02",
                "2026-11-01",
            ]
            assert any(
                "2026-11-03" in notice
                for notice in summary["notices"]
            )

            latest = player.get_recent_effective_training_days_summary(
                limit=1
            )

            assert latest["training_days"] == 1
            assert latest["shots"] == 5
            assert latest["made"] == 3
            assert latest["percentage"] == 60.0
    finally:
        engine.dispose()