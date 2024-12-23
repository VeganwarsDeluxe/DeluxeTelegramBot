import DeluxeMod.content
from DeluxeMod.Entities.NeuroRat import NeuroRat
from VegansDeluxe.core import ls

from Matches.BaseMatch import BaseMatch


class NeuroRatMatch(BaseMatch):
    name = ls("neuro")  # TODO: Localization!

    def __init__(self, chat_id, bot, engine):
        super().__init__(chat_id, bot, engine)

        self.rats = 0

    async def join_session(self, user_id, user_name):
        player = await super().join_session(user_id, user_name)
        player.team = 'players'
        if self.rats == 1:
            return

        self.rats += 1
        elemental = NeuroRat(self.id, name="NeuroRat 1.0".format(self.rats))
        self.session.attach_entity(elemental)
        await self.engine.attach_states(elemental, DeluxeMod.content.all_states)
