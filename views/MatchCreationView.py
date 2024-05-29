from telebot import types

from game.Matches.BaseMatch import BaseMatch
from startup import bot
from core.View import View


class MatchCreationView(View):
    def __init__(self, match: BaseMatch):
        super().__init__()

        self.match = match

    def get_text(self):
        return f'Игра: {self.match.name}\n\nУчастники:'

    def get_keyboard(self):
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(text='♿️Вступить в игру', url=bot.get_deep_link(f"jg_{self.match.id}")))
        kb.add(types.InlineKeyboardButton(text='▶️Запустить игру', callback_data="vd_go"))

        return kb
