from aiogram import Bot

from game.Matches.BaseMatch import BaseMatch
from startup import mm
from views.MatchCreationView import MatchCreationView
from views.MatchExistsView import MatchExistsView


class MatchCreationFlow:
    def __init__(self, chat_id: int, match: type[BaseMatch]):
        self.chat_id = chat_id
        self.mm = mm
        self.match = match

    async def execute(self, bot: Bot, locale=""):
        match = self.mm.get_match(self.chat_id)

        if match:
            view = MatchExistsView(match)
            await match.lobby_message.reply(view.get_text())
            return

        match = self.match(self.chat_id, bot)
        await match.init_async()

        match.locale = locale
        self.mm.attach_match(match)

        view = MatchCreationView(match)

        m = await bot.send_message(self.chat_id, view.get_text(), reply_markup=await view.get_keyboard(bot))
        match.lobby_message = m
