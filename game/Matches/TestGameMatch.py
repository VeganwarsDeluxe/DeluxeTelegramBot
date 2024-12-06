from VegansDeluxe.core import ls

import game.content
from game.Entities.Cow import Cow
from game.Matches.BaseMatch import BaseMatch


class TestGameMatch(BaseMatch):
    name = ls("matches.test_game")

    def __init__(self, chat_id, bot, engine):
        super().__init__(chat_id, bot, engine)

        self.skill_number = len(game.content.all_skills)
        self.weapon_number = len(game.content.all_weapons)

    async def init_async(self):
        await super().init_async()
        cow = Cow(self.id)
        self.session.attach_entity(cow)
        await self.engine.attach_states(cow, game.content.all_states)

    async def choose_items(self):
        for player in self.not_chosen_items:
            for item_type in game.content.all_items:
                item = item_type()
                for _ in range(100):
                    player.items.append(item)

            player.chose_items = True
            if player.npc:
                continue
            await self.bot.send_message(player.user_id, ls("matches.test_game.items").localize(player.locale))
