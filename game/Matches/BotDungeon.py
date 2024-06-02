from game.Entities.Beast import Beast
from game.Entities.Elemental import Elemental
from game.Entities.Slime import Slime
from game.Matches.BaseMatch import BaseMatch


class BotDungeon(BaseMatch):
    name = "Комната 19 Замка Взрывов"

    def __init__(self, chat_id):
        super().__init__(chat_id)

        elemental = Elemental(self.id)
        self.session.attach_entity(elemental)
        elemental.init_states()

        beast = Beast(self.id)
        self.session.attach_entity(beast)
        beast.init_states()

        slime = Slime(self.id)
        self.session.attach_entity(slime)
        slime.init_states()

    def join_session(self, user_id, user_name):
        player = super().join_session(user_id, user_name)
        player.team = 'players'

