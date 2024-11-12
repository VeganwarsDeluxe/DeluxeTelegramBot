from VegansDeluxe.core import AttachedAction
from VegansDeluxe.core.Actions.EntityActions import ReloadAction, SkipTurnAction, ApproachAction
from VegansDeluxe.core.Entities.Entity import Entity


class TelegramEntity(Entity):
    def __init__(self, session_id: str, user_name, user_id, code=''):
        super().__init__(session_id)
        self.id = str(user_id)

        self.name = user_name
        self.npc = False  # to differentiate humans and bots
        self.locale = code

        self.chose_weapon = False
        self.chose_skills = False
        self.skill_cycle = 0
        self.chose_items = False
        self.ready = False

    @property
    def user_id(self):
        return int(self.id)

    async def choose_act(self, session):  # method for NPCs
        pass

    def pre_move(self):
        super().pre_move()
        if not self.dead:
            self.ready = False


@AttachedAction(TelegramEntity)
class ApproachAction(ApproachAction):
    pass


@AttachedAction(TelegramEntity)
class ReloadAction(ReloadAction):
    pass


@AttachedAction(TelegramEntity)
class SkipTurnAction(SkipTurnAction):
    pass
