from aiogram import Bot


class View:
    def __init__(self, parse_mode="Markdown"):
        self.parse_mode = parse_mode
        pass

    def get_text(self):
        pass

    def get_keyboard(self, bot: Bot):
        pass
