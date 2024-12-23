from VegansDeluxe.core import ls

import game.content
from game.Entities.Beast import Beast
from game.Matches.BaseMatch import BaseMatch


class BeastDungeon(BaseMatch):
    name = ls("matches.beast")

    def __init__(self, chat_id, bot, engine):
        super().__init__(chat_id, bot, engine)

        self.beast_created = False

    async def join_session(self, user_id, user_name):
        player = await super().join_session(user_id, user_name)
        player.team = 'players'
        if not self.beast_created:
            self.beast_created = True
            beast = Beast(self.id)
            self.session.attach_entity(beast)
            await self.engine.attach_states(beast, game.content.all_states)
