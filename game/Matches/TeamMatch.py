from VegansDeluxe.core import ls

from game.Matches.BaseMatch import BaseMatch


class TeamMatch(BaseMatch):
    name = ls("matches.teams")

    def __init__(self, chat_id, bot):
        super().__init__(chat_id, bot)

        self.elementals = 0

