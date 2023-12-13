from typing import IO

import PyPDF2


def parse_pdf(file: IO) -> str:
    pdf = PyPDF2.PdfReader(file)
    text = ""
    for i in range(len(pdf.pages)):
        page_obj = pdf.pages[i]
        text += page_obj.extract_text()

    return text
