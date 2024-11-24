from VegansDeluxe.core import ls

import game.content
from game.Entities.Android import Android
from game.Matches.BaseMatch import BaseMatch
from startup import engine


class AndroidMatch(BaseMatch):
    name = ls("android")  # TODO: Localization!

    def __init__(self, chat_id, bot):
        super().__init__(chat_id, bot)

        self.rats = 0

    async def join_session(self, user_id, user_name):
        player = await super().join_session(user_id, user_name)
        player.team = 'players'
        if self.rats == 1:
            return

        self.rats += 1
        elemental = Android(self.id, name="🤖|Android".format(self.rats))
        self.session.attach_entity(elemental)
        await engine.attach_states(elemental, game.content.all_states)
