from pathlib import Path

import aiofiles
from aiohttp import ClientSession, FormData

from src.config import settings


async def get_recs_text(vacancy: str, cv: str) -> dict | None:
    try:
        async with ClientSession() as session:
            url = f"{settings.FASTAPI_URL}/recs/text"
            data = {"vacancy_text": vacancy, "cv_text": cv}
            async with session.post(url, json=data) as resp:
                if resp.status == 200:
                    recs = await resp.json()
                else:
                    recs = None

                return recs
    except:
        return None


async def get_recs_pdf(vacancy: str, cv: str) -> dict | None:
    try:
        async with ClientSession() as session:
            async with aiofiles.open(cv, "rb") as file:
                url = f"{settings.FASTAPI_URL}/recs/pdf"
                file_b = await file.read()

                form_data = FormData()
                form_data.add_field("vacancy_text", vacancy)
                form_data.add_field("cv_pdf", file_b, filename=Path(cv).name, content_type="application/pdf")

                async with session.post(url, data=form_data) as resp:
                    if resp.status == 200:
                        recs = await resp.json()
                    else:
                        recs = None

                    return recs
    except:
        return None
