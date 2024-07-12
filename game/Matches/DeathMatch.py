from VegansDeluxe.core import ls

from game.Entities.Elemental import Elemental
from game.Matches.BaseMatch import BaseMatch
from game.States.DeathMatchLives import DeathMatchLives
from startup import engine
import game.content


class DeathMatch(BaseMatch):
    name = "буль матч"

    def __init__(self, chat_id, bot):
        super().__init__(chat_id, bot)

    def join_session(self, user_id, user_name):
        player = super().join_session(user_id, user_name)
        engine.attach_states(player, [DeathMatchLives])
