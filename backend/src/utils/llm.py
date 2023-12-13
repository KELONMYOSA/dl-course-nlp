from src.contracts import RecsForm, RecsResult


def get_recs(form_data: RecsForm) -> RecsResult:
    test_text = f'''
Текст вакансии:
{form_data.vacancy_text}
Текст резюме:
{form_data.cv_text}
    '''

    recs = RecsResult(score=87.65, recs=test_text)

    return recs
