from telebot import types

from game.Matches.BaseMatch import BaseMatch
from startup import bot
from views.View import View


class MatchExistsView(View):
    def __init__(self, match: BaseMatch):
        super().__init__()

        self.match = match

    def get_text(self):
        if self.match.lobby:
            return 'Игра уже запущена!'
        else:
            return 'Игра уже идет!'
