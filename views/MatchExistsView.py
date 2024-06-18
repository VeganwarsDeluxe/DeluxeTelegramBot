from VegansDeluxe.core import ls

from game.Matches.BaseMatch import BaseMatch
from views.View import View


class MatchExistsView(View):
    def __init__(self, match: BaseMatch):
        super().__init__()

        self.match = match

    def get_text(self):
        if self.match.lobby:
            return ls("bot.error.game_already_launched").localize(self.match.locale)
        else:
            return ls("bot.join.game_already_started").localize(self.match.locale)
