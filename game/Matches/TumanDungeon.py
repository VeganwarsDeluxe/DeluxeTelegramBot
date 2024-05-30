from game.Entities.Beast import Beast
from game.Matches.BaseMatch import BaseMatch


class TumanDungeon(BaseMatch):
    name = "Данж с Волками"

    def __init__(self, chat_id):
        super().__init__(chat_id)

        self.beast_created = False  # Переменная для отслеживания создания волка

    def join_session(self, user_id, user_name):
        player = super().join_session(user_id, user_name)
        player.team = 'players'
        if not self.beast_created:
            self.beast_created = True
            beast = Beast(self.id, name='Зверь|🐺')  # Создание только одного волка
            self.session.attach_entity(beast)
            beast.init_states()
