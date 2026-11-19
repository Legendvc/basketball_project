from datetime import date

from pydantic import BaseModel, Field, model_validator


class TrainingUpdate(BaseModel):
    training_date: date
    shots: int = Field(ge=0, strict=True)
    made: int = Field(ge=0, strict=True)

    @model_validator(mode="after")
    def validate_counts(self):
        if self.made > self.shots:
            raise ValueError("命中次数不能大于投篮次数")

        return self


class TrainingCreate(TrainingUpdate):
    user_id: int = Field(ge=1, strict=True)


class TrainingResponse(BaseModel):
    id: int
    date: date
    shots: int
    made: int


class TrainingByDateResponse(BaseModel):
    user_id: int
    training_date: date
    records: list[TrainingResponse]

class TrainingDaySummary(BaseModel):
    date: date
    shots: int
    made: int
    percentage: float


class TrainingSummaryResponse(BaseModel):
    has_data: bool
    training_days: int
    required_training_days: int
    is_reference_only: bool
    shots: int
    made: int
    percentage: float
    days: list[TrainingDaySummary]
    warnings: list[str]
    notices: list[str]
    messages: list[str]
