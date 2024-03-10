from game.Matches.BaseMatch import BaseMatch
from game.Matches.Matchmaker import Matchmaker
from startup import bot
from views.MatchCreationView import MatchCreationView
from views.MatchExistsView import MatchExistsView


class MatchCreationFlow:
    def __init__(self, chat_id: int, mm: Matchmaker, match: type[BaseMatch]):
        self.chat_id = chat_id
        self.mm = mm
        self.match = match

    def execute(self):
        match = self.mm.get_match(self.chat_id)

        if match:
            view = MatchExistsView(match)
            bot.reply_to(match.lobby_message, view.get_text())
            return

        match = self.match(self.chat_id)
        self.mm.attach_match(match)

        view = MatchCreationView(match)
        m = bot.send_message(self.chat_id, view.get_text(), reply_markup=view.get_keyboard())
        match.lobby_message = m
