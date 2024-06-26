import random

import VegansDeluxe.core.Events.Events
from VegansDeluxe.core.Actions.Action import DecisiveAction
from VegansDeluxe.core import AttachedAction, RegisterWeapon, MeleeAttack, MeleeWeapon, Entity, Enemies, RegisterEvent, \
    EventContext, Session, ls
from VegansDeluxe.core import OwnOnly
from VegansDeluxe.rebuild import DamageThreshold, Aflame

from startup import engine
from .Dummy import Dummy
from .TelegramEntity import TelegramEntity
from VegansDeluxe.core.utils import percentage_chance


class Slime(Dummy):
    def __init__(self, session_id: str, name=ls("slime.name")):
        super().__init__(session_id, name)

        self.weapon = SlimeWeapon(session_id, self.id)

        self.hp = 3
        self.max_hp = 3
        self.max_energy = 5

        self.team = 'slimes'

        @RegisterEvent(self.session_id, event=VegansDeluxe.core.Events.PostActionsGameEvent)
        def post_actions(context: EventContext[VegansDeluxe.core.Events.PostActionsGameEvent]):
            self.get_state(Aflame.id).extinguished = True

    def choose_act(self, session: Session[TelegramEntity]):
        if session.turn == 1:
            self.get_state(DamageThreshold.id).threshold = 5

        if not self.weapon:
            self.weapon = SlimeWeapon(self.session_id, self.id)

        super().choose_act(session)

        if self.nearby_entities != list(filter(lambda t: t != self, session.entities)) and percentage_chance(75):
            engine.action_manager.queue_action(session, self, SlimeApproach.id)
            return

        if self.energy == 0:
            engine.action_manager.queue_action(session, self, SlimeReload.id)
            return

        if percentage_chance(50):
            engine.action_manager.queue_action(session, self, SlimeEvade.id)
            return
        else:
            attack = engine.action_manager.get_action(session, self, SlimeAttack.id)
            attack.target = random.choice(attack.targets)
            engine.action_manager.queue_action_instance(attack)
            return

        # engine.action_manager.queue_action(session, self, SlimeSlop.id)


@AttachedAction(Slime)
class SlimeApproach(DecisiveAction):
    id = 'slime_approach'
    name = ls("slime.approach.name")
    target_type = OwnOnly()

    def func(self, source, target):
        source.nearby_entities = list(filter(lambda t: t != source, self.session.entities))
        for entity in source.nearby_entities:
            entity.nearby_entities.append(source) if source not in entity.nearby_entities else None
        self.session.say(ls("slime.approach.text").format(source.name))


@AttachedAction(Slime)
class SlimeReload(DecisiveAction):
    id = 'slime_reload'
    name = ls('slime.reload.name')
    target_type = OwnOnly()

    def func(self, source, target):
        self.session.say(ls("slime.reload.text").format(source.name, source.max_energy))
        source.energy = source.max_energy


@AttachedAction(Slime)
class SlimeEvade(DecisiveAction):
    id = 'slime_evade'
    name = ls("slime.evade.name")
    target_type = OwnOnly()

    def func(self, source, target):
        self.source.inbound_accuracy_bonus = -5
        self.session.say(ls("slime.evade.text").format(source.name))


@AttachedAction(Slime)
class SlimeSlop(DecisiveAction):
    id = 'slime_slop'
    name = ls("slime.slop.name")
    target_type = OwnOnly()

    def func(self, source, target):
        self.session.say(ls("slime.slop.text").format(source.name))


@RegisterWeapon
class SlimeWeapon(MeleeWeapon):
    id = 'slime_weapon'
    name = ls('slime.weapon.name')

    cubes = 3
    damage_bonus = 0
    energy_cost = 2
    accuracy_bonus = 0


@AttachedAction(SlimeWeapon)
class SlimeAttack(MeleeAttack):
    id = 'slime_attack'
    name = ls("slime.attack.name")
    target_type = Enemies()

    def __init__(self, *args):

        super().__init__(*args)
        self.ATTACK_MESSAGE = ls("slime.weapon.attack")
        self.MISS_MESSAGE = ls("slime.weapon.miss")

    def func(self, source: Slime, target: Entity):
        damage = super().func(source, target)
        if not damage:
            return

        target.energy = max(0, target.energy - 1)
        if target.energy == 0:
            source.max_energy += 1
            source.energy = source.max_energy
            self.session.say(ls("slime.growth.text").format(source.name, source.max_energy))
