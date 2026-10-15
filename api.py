from fastapi import FastAPI
from player import Player
from pydantic import BaseModel

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

@app.get("/training-summary")
def get_training_summary():

    player = Player.load_from_json()

    return player.get_recent_effective_training_days_summary()