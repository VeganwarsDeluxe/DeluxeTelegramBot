from VegansDeluxe.core import ls

import game.content
from game.Entities.Guardian import Guardian
from game.Matches.BaseMatch import BaseMatch


class GuardianDungeon(BaseMatch):
    name = ls("matches.guardian")

    def __init__(self, chat_id, bot, engine):
        super().__init__(chat_id, bot, engine)

        self.guardian_created = False

    async def join_session(self, user_id, user_name):
        player = await super().join_session(user_id, user_name)
        player.team = 'players'
        if not self.guardian_created:
            self.guardian_created = True
            guardian = Guardian(self.id)
            self.session.attach_entity(guardian)
            await self.engine.attach_states(guardian, game.content.all_states)
