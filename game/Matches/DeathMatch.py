from game.Matches.BaseMatch import BaseMatch
from game.States.DeathMatchLives import DeathMatchLives
from startup import engine


class DeathMatch(BaseMatch):
    name = "буль матч"

    async def join_session(self, user_id, user_name):
        player = await super().join_session(user_id, user_name)
        await engine.attach_states(player, [DeathMatchLives])
