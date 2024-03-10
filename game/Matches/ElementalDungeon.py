from game.Entities.Elementalis import Elemental
from game.Matches.BaseMatch import BaseMatch


class ElementalDungeon(BaseMatch):
    name = "Данж с Елементалем"

    def __init__(self, chat_id):
        super().__init__(chat_id)

        self.elementals = 0

    def join_session(self, user_id, user_name):
        player = super().join_session(user_id, user_name)
        player.team = 'players'
        if self.elementals == 1:
            return

        self.elementals += 1
        elemental = Elemental(self.id, name=f'Веган Елементаль {self.elementals}|🌪')
        self.session.attach_entity(elemental)
        elemental.init_states()
