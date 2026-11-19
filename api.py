from datetime import date

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from api_orm_demo import app as orm_app, get_db
from models import User
from player import Player
from training_repository import create_training as insert_training
from training_repository import get_training_by_date
from training_service import get_training_summary as build_training_summary
from utils import calculate_percentage

app = FastAPI()
app.mount("/v2", orm_app)

class PlayerResponse(BaseModel):
    name: str
    age: int
    position: str
    percentage: float
    level: str

@app.get("/")
def home():
    return {
         "project": "basketball_project",
         "version": "1.0",
         "status": "running"
    }

@app.get("/player", response_model=PlayerResponse)
def get_player():

    player = Player.load_from_json()

    return {
        "name": player.name,
        "age": player.age,
        "position": player.position,
        "percentage": player.get_percentage(),
        "level": player.get_level()
    }
class TrainingRequest(BaseModel):
    training_date: date
    shots: int = Field(ge=0, strict=True)
    made: int = Field(ge=0, strict=True)

    @model_validator(mode="after")
    def validate_training(self):
        if self.made > self.shots:
            raise ValueError("命中次数不能大于投篮次数")

        return self


def get_legacy_user_id(session: Session) -> int:
    username = Player.load_from_json().name
    user_id = session.scalar(select(User.id).where(User.username == username))
    if user_id is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user_id


@app.get("/training-summary")
def get_training_summary(
    limit: int = Query(default=5, ge=1),
    session: Session = Depends(get_db),
):
    return build_training_summary(
        session=session,
        user_id=get_legacy_user_id(session),
        limit=limit,
    )


@app.post("/training", status_code=201)
def create_training(
    training: TrainingRequest,
    session: Session = Depends(get_db),
):
    with session.begin():
        row = insert_training(
            session=session,
            training_date=training.training_date.isoformat(),
            shots=training.shots,
            made=training.made,
            user_id=get_legacy_user_id(session),
        )
        record_id = row.id
        record = {
            "date": row.date,
            "shots": row.shots,
            "made": row.made,
            "percentage": calculate_percentage(row.made, row.shots),
        }

    return {
        "message": "训练记录保存成功",
        "training": record,
        "record_id": record_id
    }


@app.get("/training-by-date")
def read_training_by_date(
    training_date: date,
    session: Session = Depends(get_db),
):
    rows = get_training_by_date(
        session=session,
        training_date=training_date.isoformat(),
        user_id=get_legacy_user_id(session),
    )

    return {
        "training_date": training_date.isoformat(),
        "records": [
            {
                "id": row.id,
                "date": row.date,
                "shots": row.shots,
                "made": row.made,
            }
            for row in rows
        ],
    }
