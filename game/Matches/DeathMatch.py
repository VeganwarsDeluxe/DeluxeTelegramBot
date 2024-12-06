from game.Matches.BaseMatch import BaseMatch
from game.States.DeathMatchLives import DeathMatchLives


class DeathMatch(BaseMatch):
    # TODO: Finish DeathMatch from Rebuild.
    name = ""

    async def join_session(self, user_id, user_name):
        player = await super().join_session(user_id, user_name)
        await self.engine.attach_states(player, [DeathMatchLives])
