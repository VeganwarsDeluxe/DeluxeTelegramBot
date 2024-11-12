from VegansDeluxe.core import ls

import game.content
from game.Entities.Slime import Slime
from game.Matches.BaseMatch import BaseMatch
from startup import engine


class SlimeDungeon(BaseMatch):
    name = ls("matches.slimes")

    def __init__(self, chat_id, bot):
        super().__init__(chat_id, bot)

        self.slimes = 0

    async def join_session(self, user_id, user_name):
        player = await super().join_session(user_id, user_name)
        player.team = 'players'
        # if self.slimes == 1:
        #     return
        for _ in range(2):
            self.slimes += 1
            slime = Slime(self.id, name=ls("slime.number").format(self.slimes))
            self.session.attach_entity(slime)
            await engine.attach_states(slime, game.content.all_states)
