from VegansDeluxe.core import ls
from telebot import types

from handlers.callbacks.other import StartGame
from game.Matches.BaseMatch import BaseMatch
from startup import bot
from views.View import View


class MatchCreationView(View):
    def __init__(self, match: BaseMatch):
        super().__init__()

        self.match = match

    def get_text(self):
        return (f'{ls("bot.lobby.game").localize(self.match.locale)} {self.match.name}\n\n'
                f'{ls("bot.lobby.players").localize(self.match.locale)}')

    def get_keyboard(self):
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(text=ls("bot.button.join").localize(self.match.locale),
                                          url=bot.get_deep_link(f"jg_{self.match.id}")))
        kb.add(types.InlineKeyboardButton(text=ls("bot.button.start").localize(self.match.locale),
                                          callback_data=StartGame().pack()))

        return kb
