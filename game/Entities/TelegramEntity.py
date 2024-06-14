from VegansDeluxe.core.Actions.Action import DecisiveAction
from VegansDeluxe.core import AttachedAction, ls
from VegansDeluxe.core.Actions.EntityActions import SkipActionGameEvent, ReloadAction, SkipTurnAction, ApproachAction
from VegansDeluxe.core.Entities.Entity import Entity

from VegansDeluxe.core import OwnOnly


class TelegramEntity(Entity):
    def __init__(self, session_id: str, user_name, user_id):
        super().__init__(session_id)
        self.id = str(user_id)

        self.name = user_name
        self.npc = False  # to differentiate humans and bots
        self.locale = ''  # TODO: PASS CODE HERE

        self.chose_weapon = False
        self.chose_skills = False
        self.skill_cycle = 0
        self.chose_items = False
        self.ready = False

    @property
    def user_id(self):
        return int(self.id)

    def choose_act(self, session):  # method for AI
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
    name = ls("entity.reload.name")


@AttachedAction(TelegramEntity)
class SkipTurnAction(SkipTurnAction):
    pass
