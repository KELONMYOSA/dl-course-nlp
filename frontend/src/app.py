import asyncio
import flet


async def main(page: flet.Page):
    page.title = "Team 26"
    page.horizontal_alignment = flet.CrossAxisAlignment.CENTER
    page.scroll = flet.ScrollMode.AUTO

    async def on_refresh(e):
        vacancy_input_container.value = None
        await on_text_select(None)

    page.on_connect = on_refresh

    async def on_back(e):
        await page.clean_async()
        await page.add_async(view)

    async def on_submit(e):
        await page.clean_async()
        result_text = flet.TextField(label="Рекомендации", read_only=True, value=" ")
        await page.add_async(
            flet.Column(
                width=page.width / 2, spacing=30, controls=[flet.FilledButton("Назад", on_click=on_back), result_text]
            )
        )

        result = "Это импровизированный текст который выдает модель"
        cur_result = ""

        for char in result:
            await asyncio.sleep(0.01)
            cur_result += char
            result_text.value = cur_result
            await page.update_async()

    async def on_pdf_select(e):
        cv_input_text_button.disabled = False
        cv_input_pdf_button.disabled = True

        async def pick_files_result(ex: flet.FilePickerResultEvent):
            if ex.files:
                selected_files.value = ex.files[0].name
                await selected_files.update_async()

        async def pick_files(ex):
            await pick_files_dialog.pick_files_async(allow_multiple=False, allowed_extensions=["pdf"])

        pick_files_dialog = flet.FilePicker(on_result=pick_files_result)
        selected_files = flet.Text()
        page.overlay.append(pick_files_dialog)

        await page.update_async()

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

    async def on_text_select(e):
        cv_input_text_button.disabled = True
        cv_input_pdf_button.disabled = False
        cv_input_container.controls = [flet.TextField(label="Текст резюме", multiline=True, max_lines=15)]
        await page.update_async()

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
        flet.FilledButton("Далее", on_click=on_submit),
    ]

    view = flet.Column(width=page.width / 2, controls=main_page_controls)

    await page.add_async(view)
