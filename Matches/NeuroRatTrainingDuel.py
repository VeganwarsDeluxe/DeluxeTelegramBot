import DeluxeMod.content
from DeluxeMod.Entities.NeuroRat import NeuroRat
from VegansDeluxe.core import ls

from Matches.BaseMatch import BaseMatch


class NeuroRatTrainingDuel(BaseMatch):
    name = ls("neuro")  # TODO: Localization!

    def __init__(self, bot, engine):
        super().__init__(0, bot, engine)

        self.rats = 0

    async def add_rats(self, rat_1_id, rat_2_id):
        rat_1 = NeuroRat(self.id, name=f"{rat_1_id}", rat_id=f"{rat_1_id}")
        self.session.attach_entity(rat_1)
        await self.engine.attach_states(rat_1, DeluxeMod.content.all_states)

        rat_2 = NeuroRat(self.id, name=f"{rat_2_id}", rat_id=f"{rat_2_id}")
        self.session.attach_entity(rat_2)
        await self.engine.attach_states(rat_2, DeluxeMod.content.all_states)
