from fastapi import FastAPI
from player import Player
from db_utils import get_training_by_date
from pydantic import BaseModel, Field, model_validator
from datetime import date

app = FastAPI()

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

@app.get("/training-summary")
def get_training_summary():

    player = Player.load_from_json()

    return player.get_recent_effective_training_days_summary()

@app.post("/training", status_code=201)
def create_training(training: TrainingRequest):
    player = Player.load_from_json()

    record = player.add_training_record(
        training_date=training.training_date,
        shots=training.shots,
        made=training.made
    )

    player.save_to_json()

    return {
        "message": "训练记录保存成功",
        "training": record
    }

@app.get("/training-by-date")
def read_training_by_date(training_date: date):
    rows = get_training_by_date(training_date.isoformat())

    return {
        "training_date": training_date.isoformat(),
        "records": [
        {
            "id": row["id"],
            "date": row["date"],
            "shots": row["shots"],
            "made": row["made"]
       }
        for row in rows
       ]
    }
