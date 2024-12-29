import DeluxeMod.content
from DeluxeMod.Entities.Cow import Cow
from VegansDeluxe.core import ls

from Matches.BaseMatch import BaseMatch


class TestGameMatch(BaseMatch):
    name = ls("matches.test_game")

    def __init__(self, chat_id, bot, engine):
        super().__init__(chat_id, bot, engine)

        self.skill_number = len(DeluxeMod.content.all_skills)
        self.weapon_number = len(DeluxeMod.content.all_weapons)

    async def init_async(self):
        await super().init_async()
        cow = Cow(self.id)
        self.session.attach_entity(cow)
        await self.engine.attach_states(cow, DeluxeMod.content.all_states)

        # confucius = FireAutomaton(session_id=self.session.id)
        # self.session.attach_entity(confucius)
        # await self.engine.attach_states(confucius, DeluxeMod.content.all_states)

    async def distribute_starting_items(self):
        for player in self.session.entities:
            for item_type in DeluxeMod.content.all_items:
                item = item_type()
                for _ in range(100):
                    player.items.append(item)

            if player.type == 'npc':
                continue
            await self.bot.send_message(player.user_id, ls("matches.test_game.items").localize(player.locale))
