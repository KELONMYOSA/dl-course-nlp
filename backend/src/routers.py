from fastapi import APIRouter, UploadFile, File, Form

from src.contracts import RecsResult, RecsForm
from src.utils.llm import get_recs
from src.utils.pdf import parse_pdf

router = APIRouter()


@router.post("/recs/text", response_model=RecsResult, tags=["Recommendations"])
async def recs_text(form_data: RecsForm):
    return get_recs(form_data)


@router.post("/recs/pdf", response_model=RecsResult, tags=["Recommendations"])
async def recs_pdf(vacancy_text: str = Form(...), cv_pdf: UploadFile = File(...)):
    cv_text = parse_pdf(cv_pdf.file)
    recs = RecsForm(vacancy_text=vacancy_text, cv_text=cv_text)

    return get_recs(recs)
