from pydantic import BaseModel


class RecsForm(BaseModel):
    vacancy_text: str
    cv_text: str


class RecsResult(BaseModel):
    score: float
    recs: str
