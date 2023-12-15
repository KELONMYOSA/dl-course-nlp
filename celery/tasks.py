import os

from celery import Celery
from model_utils import *
from prompts import *

RMQ_URL = os.getenv("RMQ_URL")
REDIS_URL = os.getenv("REDIS_URL")

celery_app = Celery("tasks", broker=RMQ_URL, backend=REDIS_URL)

# define llm pipeline component
llm = load_intel_model()
agent_prompts = get_candidates_prompt()
vacancy_prompt = get_vacancies_prompt()
recs_prompt = get_recs_prompt()
score_prompt = get_score_prompt()


@celery_app.task(name="llm.recs")
def process_recs(recs_form: dict) -> dict:
    vacancy = recs_form["vacancy_text"]
    cv = recs_form["cv_text"]

    candidate_info = get_candidate_info(agent_prompts, cv, llm)
    key_vacancy = get_vacancy_info(vacancy_prompt, vacancy, llm)
    recs_pred = get_recs(recs_prompt, candidate_info, key_vacancy, llm)
    score = float(get_score(score_prompt, candidate_info, key_vacancy, recs_pred, llm))

    return {"score": score, "recs": recs_pred}
