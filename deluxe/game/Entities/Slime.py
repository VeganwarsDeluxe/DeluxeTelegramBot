import random

from VegansDeluxe.core.Actions.Action import DecisiveAction
from VegansDeluxe.core import AttachedAction, RegisterWeapon, MeleeAttack, MeleeWeapon, Entity, Enemies
from VegansDeluxe.core import OwnOnly
from deluxe.startup import engine
from .Dummy import Dummy
from ..Sessions.TelegramSession import TelegramSession
from VegansDeluxe.core.utils import percentage_chance


class Slime(Dummy):
    def __init__(self, session_id: str, name='Слизень|🥗'):
        super().__init__(session_id, name)

        self.weapon = SlimeWeapon(session_id, self.id)

        self.hp = 3
        self.max_hp = 3
        self.max_energy = 5

        self.team = 'slimes'

    def choose_act(self, session: TelegramSession):
        if not self.weapon:
            self.weapon = SlimeWeapon(self.session_id, self.id)

        super().choose_act(session)

        if self.nearby_entities != list(filter(lambda t: t != self, session.entities)):
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
    name = 'Подпрыгнуть'
    target_type = OwnOnly()

    def func(self, source, target):
        source.nearby_entities = list(filter(lambda t: t != source, self.session.entities))
        for entity in source.nearby_entities:
            entity.nearby_entities.append(source) if source not in entity.nearby_entities else None
        self.session.say(f'👣|{source.name} подпрыгивает ближе!')


@AttachedAction(Slime)
class SlimeReload(DecisiveAction):
    id = 'slime_reload'
    name = 'Устало похлюпать'
    target_type = OwnOnly()

    def func(self, source, target):
        self.session.say(f'💧️|{source.name} устало хлюпает. Енергия восстановлена ({source.max_energy})!')
        source.energy = source.max_energy


@AttachedAction(Slime)
class SlimeEvade(DecisiveAction):
    id = 'slime_evade'
    name = 'Ускользнуть'
    target_type = OwnOnly()

    def func(self, source, target):
        self.source.inbound_accuracy_bonus = -5
        self.session.say(f'🩲|{source.name} ускользает.')


@AttachedAction(Slime)
class SlimeSlop(DecisiveAction):
    id = 'slime_slop'
    name = 'Хлюпать'
    target_type = OwnOnly()

    def func(self, source, target):
        self.session.say(f"🩲|{source.name} хлюпает.")


@RegisterWeapon
class SlimeWeapon(MeleeWeapon):
    id = 'slime_weapon'
    name = 'Слизь'
    description = 'Хлюпанье слизня.'

    cubes = 3
    damage_bonus = 0
    energy_cost = 2
    accuracy_bonus = 0


@AttachedAction(SlimeWeapon)
class SlimeAttack(MeleeAttack):
    ATTACK_MESSAGE = "🩲|{source_name} нахлюпал на {target_name}! " \
                     "Нанесено {damage} урона."
    MISS_MESSAGE = "💨|{source_name} хлюпает на {target_name}, но не попадает."

    id = 'slime_attack'
    name = 'Хлюпнуть'
    target_type = Enemies()

    def func(self, source: Slime, target: Entity):
        super().func(source, target)
        target.energy = max(0, target.energy - 1)

        if target.energy == 0:
            source.max_energy += 1
            source.energy = source.max_energy
            self.session.say(f"🩲|{source.name} радостью дрожит, энергия востановлена и увеличена на 1!")
