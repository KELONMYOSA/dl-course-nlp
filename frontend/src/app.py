import flet


async def main(page: flet.Page):
    page.title = "Team 26"
    t = flet.Text(value="Hello, world!", color="green")
    await page.add_async(t)
