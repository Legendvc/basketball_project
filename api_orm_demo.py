from datetime import date

from fastapi import Depends, FastAPI, HTTPException, Query
from models import User
from sqlalchemy.orm import Session
from database import SessionLocal
from training_repository import create_training, get_training_by_date
from schemas import (
    TrainingCreate,
    TrainingResponse,
    TrainingByDateResponse,
)

from schemas import TrainingSummaryResponse
from training_service import get_training_summary

app = FastAPI()




def get_db():
    with SessionLocal() as session:
        yield session


@app.get(
    "/training-by-date",
    response_model=TrainingByDateResponse,
)
def read_training_by_date(
    training_date: date,
    user_id: int = Query(ge=1),
    session: Session = Depends(get_db),
):
    records = get_training_by_date(
        session,
        training_date.isoformat(),
        user_id=user_id,
    )

    return {
        "user_id": user_id,
        "training_date": training_date.isoformat(),
        "records": [
            {
                "id": record.id,
                "date": record.date,
                "shots": record.shots,
                "made": record.made,
            }
            for record in records
        ],
    }


@app.post(
    "/training",
    response_model=TrainingResponse,
    status_code=201,
)
def post_training(
    training: TrainingCreate,
    session: Session = Depends(get_db),
):
    with session.begin():
        user = session.get(User, training.user_id)
        if user is None:
            raise HTTPException(
                status_code=404,
                detail="用户不存在",
            )

        record = create_training(
            session=session,
            training_date=training.training_date.isoformat(),
            shots=training.shots,
            made=training.made,
            user_id=training.user_id,
        )

        response = TrainingResponse(
            id=record.id,
            date=record.date,
            shots=record.shots,
            made=record.made,
        )

    return response


@app.get(
    "/training-summary",
    response_model=TrainingSummaryResponse,
)
def read_training_summary(
    user_id: int = Query(ge=1),
    limit: int = Query(default=5, ge=1),
    session: Session = Depends(get_db),
):
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="用户不存在",
        )

    return get_training_summary(
        session=session,
        user_id=user_id,
        limit=limit,
    )