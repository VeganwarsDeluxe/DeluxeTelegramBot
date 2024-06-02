from VegansDeluxe.core.Actions.Action import DecisiveAction
from VegansDeluxe.core import AttachedAction, ls
from VegansDeluxe.core.Actions.EntityActions import SkipActionGameEvent
from VegansDeluxe.core.Entities.Entity import Entity

from VegansDeluxe.core import OwnOnly
from startup import engine

import game.content


class TelegramEntity(Entity):
    def __init__(self, session_id: str, user_name, user_id):
        super().__init__(session_id)
        self.id = str(user_id)

        self.name = user_name
        self.npc = False  # to differentiate humans and bots

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

    def init_states(self):
        engine.attach_states(self, game.content.all_states)

    def pre_move(self):
        super().pre_move()
        if not self.dead:
            self.ready = False


@AttachedAction(TelegramEntity)
class ApproachAction(DecisiveAction):
    id = 'approach'
    name = ls("entity.approach.name")
    target_type = OwnOnly()

    @property
    def hidden(self) -> bool:
        return self.source.nearby_entities == list(filter(lambda t: t != self.source, self.session.entities))

    def func(self, source, target):
        source.nearby_entities = list(filter(lambda t: t != source, self.session.entities))
        for entity in source.nearby_entities:
            entity.nearby_entities.append(source) if source not in entity.nearby_entities else None
        self.session.say(ls("entity.approach.text").format(source.name))


@AttachedAction(TelegramEntity)
class ReloadAction(DecisiveAction):
    id = 'reload'
    name = ls("entity.reload.name")
    target_type = OwnOnly()

    def func(self, source, target):
        source.energy = source.max_energy
        self.session.say(source.weapon.reload_text(source))


@AttachedAction(TelegramEntity)
class SkipTurnAction(DecisiveAction):
    id = 'skip'
    name = ls('entity.skip.name')
    target_type = OwnOnly()
    priority = 2

    def func(self, source, target):
        message = self.event_manager.publish(SkipActionGameEvent(self.session.id, self.session.turn, source.id))
        if not message.no_text:
            self.session.say(ls("entity.skip.text").format(source.name))
