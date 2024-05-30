import random

import VegansDeluxe.core.Events.Events
from VegansDeluxe.core.Actions.Action import DecisiveAction
from VegansDeluxe.core import AttachedAction, RegisterWeapon, MeleeAttack, MeleeWeapon, Entity, Enemies, RegisterEvent, \
    EventContext
from VegansDeluxe.core import OwnOnly
from VegansDeluxe.rebuild import DamageThreshold, Aflame

from startup import engine
from .Dummy import Dummy
from ..Sessions.TelegramSession import TelegramSession
from VegansDeluxe.core.utils import percentage_chance


# Наведіть тут порядок будь ласка.


class Beast(Dummy):
    def __init__(self, session_id: str, name='Зверь|🐺'):
        super().__init__(session_id, name)

        self.weapon = BeastWeapon(session_id, self.id)

        self.hp = 4
        self.max_hp = 4
        self.max_energy = 6

        self.team = 'Beast'

        @RegisterEvent(self.session_id, event=VegansDeluxe.core.Events.PostActionsGameEvent)
        def post_actions(context: EventContext[VegansDeluxe.core.Events.PostActionsGameEvent]):
            self.get_state(Aflame.id).extinguished = True

    def choose_act(self, session: TelegramSession):
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

        def some_function(session, target):
            # Проверяем, что у цели остался только 1 HP
            if target.hp == 1:
                # Если это так, добавляем дополнительное действие к объекту engine.action_manager
                engine.action_manager.queue_action(session, self, BeastBite.id)

        if percentage_chance(40):
            engine.action_manager.queue_action(session, self, BeastReload.id)
            return

        if self.energy == 0:
            engine.action_manager.queue_action(session, self, BeastReload.id)

        if percentage_chance(30):
            engine.action_manager.queue_action(session, self, BeastEvade.id)
            return
        else:
            attack = engine.action_manager.get_action(session, self, BeastAttack.id)
            attack.target = random.choice(attack.targets)
            engine.action_manager.queue_action_instance(attack)
            return

        # engine.action_manager.queue_action(session, self, BeastSlop.id)


@AttachedAction(Beast)
class BeastApproach(DecisiveAction):
    id = 'Beast_approach'
    name = 'Крастца'
    target_type = OwnOnly()

    def func(self, source, target):
        source.nearby_entities = list(filter(lambda t: t != source, self.session.entities))
        for entity in source.nearby_entities:
            entity.nearby_entities.append(source) if source not in entity.nearby_entities else None
        self.session.say(f'🐾|{source.name} крадётся к своей жертве ближе...')


@AttachedAction(Beast)
class BeastReload(DecisiveAction):
    id = 'Beast_reload'
    name = 'Перевести дух'
    target_type = OwnOnly()

    def func(self, source, target):
        self.session.say(f'😤|{source.name} Переводит дух. Енергия восстановлена ({source.max_energy})!')
        source.energy = source.max_energy


@AttachedAction(Beast)
class BeastEvade(DecisiveAction):
    id = 'Beast_evade'
    name = 'Резко отпрыгнуть'
    target_type = OwnOnly()

    def func(self, source, target):
        self.source.inbound_accuracy_bonus = -6
        self.session.say(f'💨|{source.name} Резко отпрыгивает назад!')


@AttachedAction(Beast)
class BeastGrowl(DecisiveAction):
    id = 'Beast_slop'
    name = 'Рычать'
    target_type = OwnOnly()

    def func(self, source, target):
        self.session.say(f"💢|{source.name} Рычит.")


@AttachedAction(Beast)
class BeastBite(DecisiveAction):
    def func(self, source: Beast, target: Entity):
        damage = super().func(source, target)
        if not damage:
            return
        target.hp = max(0, target.hp - 1)
        if target.hp == 1:
            target.hp -= 1
            self.session.say(f"❕❕|{source.name} делает стримительный прыжок к {target.name} и кусает его! Цель теряет 1♥️.")


@RegisterWeapon
class BeastWeapon(MeleeWeapon):
    id = 'Beast_weapon'
    name = 'Клыки и когти'
    description = 'Рычанье Зверя.'

    cubes = 3
    damage_bonus = 0
    energy_cost = 2
    accuracy_bonus = 1


@AttachedAction(BeastWeapon)
class BeastAttack(MeleeAttack):
    ATTACK_MESSAGE = "❕|{source_name} кусает {target_name}! " \
                     "Нанесено {damage} урона."
    MISS_MESSAGE = "💨|{source_name} кусает {target_name}, но не попадает."

    id = 'Beast_attack'
    name = 'Кусать'
    target_type = Enemies()

    def func(self, source: Beast, target: Entity):
        damage = super().func(source, target)
        if not damage:
            return
        target.hp = max(0, target.hp - 1)
        if target.hp == 1:
            target.hp -= 1
            self.session.say(f"❕❕|{source.name} делает стримительный прыжок к {target.name} и кусает его! Цель теряет 1♥️.")
