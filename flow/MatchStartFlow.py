from VegansDeluxe.core.Translator.LocalizedString import LocalizedString, ls
from aiogram import Bot

import config
from game.Matches.BaseMatch import BaseMatch
from game.Matches.Matchmaker import Matchmaker


class MatchStartFlow:
    def __init__(self, chat_id: int, user_id: int, mm: Matchmaker):
        self.chat_id = chat_id
        self.user_id = user_id
        self.mm = mm

    async def execute(self) -> LocalizedString:
        match = self.mm.get_match(self.chat_id)
        match: BaseMatch

        if not match:
            return ls("bot.join.game_not_started")

        if str(self.user_id) not in match.player_ids:
            if self.user_id not in config.admin_ids:
                return ls("bot.start.not_in_game")

        if not match.lobby:
            return ls("bot.join.game_already_started")

        match.lobby = False
        print(match.id)
        await match.choose_items()
        await match.choose_weapons()

        await match.lobby_message.reply(ls("bot.start.success").localize())
