from game.Matches.BaseMatch import BaseMatch


class ElementalDungeon(BaseMatch):
    name = "Командная игра"

    def __init__(self, chat_id):
        super().__init__(chat_id)

        self.elementals = 0

