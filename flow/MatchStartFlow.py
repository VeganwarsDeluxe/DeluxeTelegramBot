from VegansDeluxe.core.Translator.LocalizedString import LocalizedString, ls

import config
from game.Matches.Matchmaker import Matchmaker
from startup import bot


class MatchStartFlow:
    def __init__(self, chat_id: int, user_id: int, mm: Matchmaker):
        self.chat_id = chat_id
        self.user_id = user_id
        self.mm = mm

    def execute(self) -> LocalizedString:
        match = self.mm.get_match(self.chat_id)
        if not match:
            return ls("bot.join.game_not_started")

        if str(self.user_id) not in match.session.player_ids:
            if self.user_id not in config.admin_ids:
                return ls("bot.start.not_in_game")

        if not match.lobby:
            return ls("bot.join.game_already_started")

        match.lobby = False
        match.choose_items()
        match.choose_weapons()
        bot.reply_to(match.lobby_message, ls("bot.start.success").localize())
