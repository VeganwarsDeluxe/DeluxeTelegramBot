from VegansDeluxe.core import ls

import game.content
from game.Entities.Beast import Beast
from game.Entities.Elemental import Elemental
from game.Entities.Slime import Slime
from game.Matches.BaseMatch import BaseMatch
from startup import engine


class BotDungeon(BaseMatch):
    name = ls("matches.bots")

    async def init_async(self):
        await super().init_async()
        elemental = Elemental(self.id)
        self.session.attach_entity(elemental)
        await engine.attach_states(elemental, game.content.all_states)

        beast = Beast(self.id)
        self.session.attach_entity(beast)
        await engine.attach_states(beast, game.content.all_states)

        slime = Slime(self.id)
        self.session.attach_entity(slime)
        await engine.attach_states(slime, game.content.all_states)

    async def join_session(self, user_id, user_name):
        player = await super().join_session(user_id, user_name)
        player.team = 'players'

