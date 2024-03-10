from game.Entities.Slime import Slime
from game.Matches.BaseMatch import BaseMatch


class SlimeDungeon(BaseMatch):
    name = "Данж со Слаймами"

    def __init__(self, chat_id):
        super().__init__(chat_id)

        self.slimes = 0

    def join_session(self, user_id, user_name):
        player = super().join_session(user_id, user_name)
        player.team = 'players'
        # if self.slimes == 1:
        #     return
        for _ in range(2):
            self.slimes += 1
            slime = Slime(self.id, name=f'Слизень {self.slimes}|🥗')
            self.session.attach_entity(slime)
            slime.init_states()
