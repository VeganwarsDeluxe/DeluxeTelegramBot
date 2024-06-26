from VegansDeluxe.core import ls

from game.Entities.Slime import Slime
from game.Matches.BaseMatch import BaseMatch
from startup import engine
import game.content


class SlimeDungeon(BaseMatch):
    name = ls("matches.slimes")

    def __init__(self, chat_id, bot):
        super().__init__(chat_id, bot)

        self.slimes = 0

    def join_session(self, user_id, user_name):
        player = super().join_session(user_id, user_name)
        player.team = 'players'
        # if self.slimes == 1:
        #     return
        for _ in range(2):
            self.slimes += 1
            slime = Slime(self.id, name=ls("slime.number").format(self.slimes))
            self.session.attach_entity(slime)
            engine.attach_states(slime, game.content.all_states)
