from VegansDeluxe.core import ls
from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import deep_linking

from game.Matches.BaseMatch import BaseMatch
from handlers.callbacks.other import StartGame
from views.View import View


class MatchCreationView(View):
    def __init__(self, match: BaseMatch):
        super().__init__()

        self.match = match

    def get_text(self):
        return (f'{ls("bot.lobby.game").localize(self.match.locale)} {self.match.name.localize(self.match.locale)}\n\n'
                f'{ls("bot.lobby.players").localize(self.match.locale)}')

    async def get_keyboard(self, bot: Bot):
        link = deep_linking.create_deep_link((await bot.get_me()).username, "start", f"jg_{self.match.id}")

        kb = [[], []]
        kb[0].append(InlineKeyboardButton(text=ls("bot.button.join").localize(self.match.locale),
                                          url=link))
        kb[1].append(InlineKeyboardButton(text=ls("bot.button.start").localize(self.match.locale),
                                          callback_data=StartGame().pack()))

        kb = InlineKeyboardMarkup(inline_keyboard=kb)
        return kb
