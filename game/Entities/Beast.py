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


class Beast(Dummy):
    def __init__(self, session_id: str, name=ls("beast.name")):
        super().__init__(session_id, name)

        self.weapon = BeastWeapon(session_id, self.id)

        self.hp = 4
        self.max_hp = 4
        self.max_energy = 6

        self.team = 'beast'

    def choose_act(self, session: Session[TelegramEntity]):
        if session.turn == 1:
            self.get_state(DamageThreshold.id).threshold = 6

        if not self.weapon:
            self.weapon = BeastWeapon(self.session_id, self.id)

        super().choose_act(session)

        if self.nearby_entities != list(filter(lambda t: t != self, session.entities)) and percentage_chance(75):
            engine.action_manager.queue_action(session, self, BeastApproach.id)
            return

        if percentage_chance(5):
            engine.action_manager.queue_action(session, self, BeastGrowl.id)
            return

        if percentage_chance(15):
            engine.action_manager.queue_action(session, self, BeastReload.id)
            return

        if self.energy == 0:
            engine.action_manager.queue_action(session, self, BeastReload.id)
            return

        if percentage_chance(30):
            engine.action_manager.queue_action(session, self, BeastEvade.id)
            return

        targets = [entity for entity in self.nearby_entities if entity != self and entity.hp > 0]
        if targets:
            target = random.choice(targets)
            if target.hp == 1:
                attack = engine.action_manager.get_action(session, self, BeastBite.id)
                attack.target = target
                engine.action_manager.queue_action_instance(attack)
            else:
                attack = engine.action_manager.get_action(session, self, BeastAttack.id)
                attack.target = target
                engine.action_manager.queue_action_instance(attack)
        else:
            # If no valid targets, the beast reloads
            engine.action_manager.queue_action(session, self, BeastReload.id)


@AttachedAction(Beast)
class BeastApproach(DecisiveAction):
    id = 'beast_approach'
    name = ls("beast.approach.name")
    target_type = OwnOnly()

    def func(self, source, target):
        source.nearby_entities = list(filter(lambda t: t != source, self.session.entities))
        for entity in source.nearby_entities:
            if source not in entity.nearby_entities:
                entity.nearby_entities.append(source)
        self.session.say(ls("beast.approach.text").format(source.name))


@AttachedAction(Beast)
class BeastReload(DecisiveAction):
    id = 'beast_reload'
    name = ls("beast.reload.name")
    target_type = OwnOnly()

    def func(self, source, target):
        self.session.say(ls('beast.reload.text').format(source.name, source.max_energy))
        source.energy = source.max_energy


@AttachedAction(Beast)
class BeastEvade(DecisiveAction):
    id = 'beast_evade'
    name = ls("beast.evade.name")
    target_type = OwnOnly()

    def func(self, source, target):
        source.inbound_accuracy_bonus = -6
        self.session.say(ls("beast.evade.text").format(source.name))


@AttachedAction(Beast)
class BeastGrowl(DecisiveAction):
    id = 'beast_growl'
    name = ls("beast.growl.name")
    target_type = OwnOnly()

    def func(self, source, target):
        self.session.say(ls("beast.growl.text").format(source.name))


@RegisterWeapon
class BeastWeapon(MeleeWeapon):
    id = 'beast_weapon'
    name = ls("beast.weapon.name")

    cubes = 3
    damage_bonus = 0
    energy_cost = 2
    accuracy_bonus = 1


@AttachedAction(BeastWeapon)
class BeastAttack(MeleeAttack):
    id = 'beast_attack'
    name = ls("beast.attack.name")
    target_type = Enemies()

    def __init__(self, *args):

        super().__init__(*args)
        self.ATTACK_MESSAGE = ls("beast.weapon.attack")
        self.MISS_MESSAGE = ls("beast.weapon.miss")


@AttachedAction(BeastWeapon)
class BeastBite(MeleeAttack):
    id = 'beast_bite'
    name = ls("beast.bite.name")

    def func(self, source, target):
        target.hp = max(0, target.hp - 1)
        self.session.say(ls("beast.bite.text").format(source.name, target.name))
