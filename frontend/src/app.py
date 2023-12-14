import asyncio
import os
import time
from pathlib import Path

import flet

from src.utils import get_recs_pdf_token, get_recs_result, get_recs_text_token


async def main(page: flet.Page):
    page.title = "Team 26"
    page.horizontal_alignment = flet.CrossAxisAlignment.CENTER
    page.scroll = flet.ScrollMode.AUTO
    selected_pdf = None

    async def on_refresh(e):
        vacancy_input_container.value = None
        global selected_pdf
        selected_pdf = None
        await on_text_select(None)

    page.on_connect = on_refresh

    async def on_back(e):
        await page.clean_async()
        await page.add_async(view)

    """
    При нажатии на кнопку "Далее"
    """

    async def on_submit(e):
        submit_button.controls.append(flet.ProgressRing())
        submit_button.controls[0].disabled = True
        await page.update_async()

        # Проверяем, что необходимые поля не пустые
        global selected_pdf
        cv_input_is_empty = True
        cv_input_item = cv_input_container.controls[0]
        if isinstance(cv_input_item, flet.TextField):
            if cv_input_item.value:
                cv_input_is_empty = False
        else:
            if selected_pdf:
                cv_input_is_empty = False

        if len(vacancy_input_container.value) < 1 or cv_input_is_empty:
            submit_button.controls.pop(-1)
            submit_button.controls[0].disabled = False
            dlg = flet.AlertDialog(title=flet.Text("Необходимо заполнить поля с текстом вакансии и резюме!"))
            page.dialog = dlg
            dlg.open = True
            await page.update_async()
            return

        # Получаем результаты из модели
        if isinstance(cv_input_item, flet.TextField):
            task_id = await get_recs_text_token(vacancy_input_container.value, cv_input_item.value)
        else:
            task_id = await get_recs_pdf_token(vacancy_input_container.value, selected_pdf)

        result = None
        if task_id:
            for retry in range(30):
                result = await get_recs_result(task_id)
                if result:
                    break
                await asyncio.sleep(1)

        # Если ошибка запроса
        if result is None:
            submit_button.controls.pop(-1)
            submit_button.controls[0].disabled = False
            dlg = flet.AlertDialog(title=flet.Text("Ошибка сервера!"))
            page.dialog = dlg
            dlg.open = True
            await page.update_async()
            return

        # Загружаем страницу с результатами
        submit_button.controls.pop(-1)
        submit_button.controls[0].disabled = False
        await page.clean_async()
        result_text = flet.TextField(label="Рекомендации", multiline=True, read_only=True, value=" ")
        score_text = flet.Text("", size=50, text_align=flet.TextAlign.CENTER)
        await page.add_async(
            flet.Column(
                width=page.width / 2,
                spacing=30,
                controls=[
                    flet.FilledButton("Назад", on_click=on_back),
                    flet.Container(
                        content=score_text,
                        alignment=flet.alignment.center,
                        height=80,
                    ),
                    result_text,
                ],
            )
        )

        # Выводим посимвольно результат
        score = result["score"]
        text = result["recs"]
        score_text.value = f"{round(score)}/100"
        cur_text = ""
        for char in text:
            await asyncio.sleep(0.01)
            cur_text += char
            result_text.value = cur_text
            await page.update_async()

    """
    При нажатии на кнопку "PDF"
    """

    async def on_pdf_select(e):
        cv_input_text_button.disabled = False
        cv_input_pdf_button.disabled = True

        async def pick_files_result(ex: flet.FilePickerResultEvent):
            if ex.files:
                file_name = ex.files[0].name
                file_path = f"/cv/{int(time.time())}/{file_name}"
                await pick_files_dialog.upload_async(
                    [flet.FilePickerUploadFile(file_name, upload_url=await page.get_upload_url_async(file_path, 600))]
                )

                global selected_pdf
                selected_pdf = Path(os.getcwd(), "src/assets/uploads" + file_path)
                selected_files.value = file_name
                await selected_files.update_async()

        async def pick_files(ex):
            await pick_files_dialog.pick_files_async(allow_multiple=False, allowed_extensions=["pdf"])

        pick_files_dialog = flet.FilePicker(on_result=pick_files_result)
        selected_files = flet.Text()
        page.overlay.append(pick_files_dialog)

        cv_input_container.controls = [
            flet.Row(
                [
                    flet.ElevatedButton(
                        "Загрузить резюме",
                        icon=flet.icons.UPLOAD_FILE,
                        on_click=pick_files,
                    ),
                    selected_files,
                ]
            )
        ]

        await page.update_async()

    """
    При нажатии на кнопку "Текст"
    """

    async def on_text_select(e):
        cv_input_text_button.disabled = True
        cv_input_pdf_button.disabled = False
        global selected_pdf
        selected_pdf = None
        cv_input_container.controls = [flet.TextField(label="Текст резюме", multiline=True, max_lines=15)]
        await page.update_async()

    """
    Начальное состояние элементов на странице
    """
    cv_input_text_button = flet.ElevatedButton(
        text="Текст",
        expand=True,
        on_click=on_text_select,
        disabled=True,
        style=flet.ButtonStyle(
            shape=flet.RoundedRectangleBorder(
                radius=flet.BorderRadius(top_left=10, bottom_left=10, top_right=0, bottom_right=0)
            )
        ),
    )

    cv_input_pdf_button = flet.ElevatedButton(
        text="PDF",
        expand=True,
        on_click=on_pdf_select,
        style=flet.ButtonStyle(
            shape=flet.RoundedRectangleBorder(
                radius=flet.BorderRadius(top_left=0, bottom_left=0, top_right=10, bottom_right=10)
            )
        ),
    )

    vacancy_input_container = flet.TextField(label="Текст вакансии", multiline=True, max_lines=15)
    cv_input_container = flet.Column(controls=[flet.TextField(label="Текст резюме", multiline=True, max_lines=15)])
    submit_button = flet.Row(controls=[flet.FilledButton("Далее", on_click=on_submit)])

    main_page_controls = [
        flet.Container(
            content=flet.Text(value="Job Match", style=flet.TextThemeStyle.HEADLINE_MEDIUM, color=flet.colors.BLUE_600),
            alignment=flet.alignment.center,
            height=80,
        ),
        flet.Divider(),
        vacancy_input_container,
        flet.Divider(),
        flet.Row(spacing=-0, controls=[cv_input_text_button, cv_input_pdf_button]),
        cv_input_container,
        flet.Divider(),
        submit_button,
    ]

    view = flet.Column(width=page.width / 2, controls=main_page_controls)

    await page.add_async(view)
