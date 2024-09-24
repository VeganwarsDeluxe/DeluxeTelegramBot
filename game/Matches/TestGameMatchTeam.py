from VegansDeluxe.core import ls

import game.content
from game.Entities.Cow import Cow
from game.Matches.BaseMatch import BaseMatch
from startup import engine


class TestGameMatchTeam(BaseMatch):
    name = ls("matches.test_game_team")

    def __init__(self, chat_id, bot):
        super().__init__(chat_id, bot)

        self.skill_number = len(game.content.all_skills)
        self.weapon_number = len(game.content.all_weapons)

    async def init_async(self):
        await super().init_async()
        cow = Cow(self.id)
        self.session.attach_entity(cow)
        await engine.attach_states(cow, game.content.all_states)

    async def choose_items(self):
        for player in self.not_chosen_items:
            for item_type in game.content.all_items:
                item = item_type()
                for _ in range(100):
                    player.items.append(item)

            player.chose_items = True
            if player.npc:
                continue
            await self.bot.send_message(player.user_id, ls("test_game.items").localize(player.locale))

    async def join_session(self, user_id, user_name):
        player = super().join_session(user_id, user_name)
        player.team = 'players'
