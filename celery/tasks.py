import os
import time

from celery import Celery

RMQ_URL = os.getenv("RMQ_URL")
REDIS_URL = os.getenv("REDIS_URL")

celery_app = Celery("tasks", broker=RMQ_URL, backend=REDIS_URL)


@celery_app.task(name="llm.recs")
def process_recs(recs_form: dict) -> dict:
    vacancy = recs_form["vacancy_text"]
    cv = recs_form["cv_text"]

    example_score = 87.65
    example_text = f"""
Текст вакансии:
{vacancy}
Текст резюме:
{cv}
        """
    time.sleep(5)

    return {"score": example_score, "recs": example_text}
