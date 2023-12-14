from fastapi import APIRouter, File, Form, UploadFile

from src.contracts import RecsForm, RecsResult
from src.utils.celery_config import celery_app, get_task_result
from src.utils.pdf import parse_pdf

router = APIRouter()


@router.post("/recs/text", tags=["Recommendations"])
async def recs_text(form_data: RecsForm):
    task = celery_app.send_task("llm.recs", kwargs={"recs_form": form_data.model_dump()})
    task_id = task.id

    return {"message": "Задача успешно создана", "task_id": task_id}


@router.post("/recs/pdf", tags=["Recommendations"])
async def recs_pdf(vacancy_text: str = Form(...), cv_pdf: UploadFile = File(...)):
    cv_text = parse_pdf(cv_pdf.file)
    form_data = RecsForm(vacancy_text=vacancy_text, cv_text=cv_text)

    task = celery_app.send_task("llm.recs", kwargs={"recs_form": form_data.model_dump()})
    task_id = task.id

    return {"message": "Задача успешно создана", "task_id": task_id}


@router.get("/recs/result/{task_id}", response_model=RecsResult | None, tags=["Recommendations"])
async def recs_result(task_id: str):
    task_result = get_task_result(task_id)
    if task_result["status"] == "SUCCESS":
        task_result = task_result["result"]
        recs = RecsResult(score=task_result["score"], recs=task_result["recs"])
        return recs
    else:
        return None
