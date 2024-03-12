from VegansDeluxe import rebuild
from game.Entities.Cow import Cow
from game.Matches.BaseMatch import BaseMatch


class TestGameMatch(BaseMatch):
    name = "Тестовая игра"

    def __init__(self, chat_id):
        super().__init__(chat_id)

        self.skill_number = len(rebuild.all_skills)
        self.weapon_number = len(rebuild.all_weapons)

        cow = Cow(self.id)
        self.session.attach_entity(cow)
        cow.init_states()

    def choose_items(self):
        for player in self.session.not_chosen_items:
            for item_type in rebuild.all_items:
                item = item_type()
                for _ in range(100):
                    player.items.append(item)

            player.chose_items = True
            if player.npc:
                continue
            self.bot.send_message(player.user_id, f'Ваши предметы: по 100 каждого.')