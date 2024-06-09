from VegansDeluxe.core import ls

from game.Entities.Cow import Cow
from game.Matches.BaseMatch import BaseMatch
import game.content
from startup import engine


class TestGameMatch(BaseMatch):
    name = ls("matches.test_game")

    def __init__(self, chat_id, bot):
        super().__init__(chat_id, bot)

        self.skill_number = len(game.content.all_skills)
        self.weapon_number = len(game.content.all_weapons)

        cow = Cow(self.id)
        self.session.attach_entity(cow)
        engine.attach_states(cow, game.content.all_states)

    def choose_items(self):
        for player in self.not_chosen_items:
            for item_type in game.content.all_items:
                item = item_type()
                for _ in range(100):
                    player.items.append(item)

            player.chose_items = True
            if player.npc:
                continue
            self.bot.send_message(player.user_id, ls("test_game.items"))
