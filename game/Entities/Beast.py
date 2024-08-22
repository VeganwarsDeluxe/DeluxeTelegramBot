import random

import VegansDeluxe.core.Events.Events
from VegansDeluxe.core.Actions.Action import DecisiveAction
from VegansDeluxe.core import AttachedAction, RegisterWeapon, MeleeAttack, MeleeWeapon, Entity, Enemies, RegisterEvent, \
    EventContext, Session
from VegansDeluxe.core import OwnOnly
from VegansDeluxe.rebuild import DamageThreshold, Aflame

from startup import engine
from .Dummy import Dummy
from .TelegramEntity import TelegramEntity
from VegansDeluxe.core.utils import percentage_chance


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

    def choose_act(self, session: Session):
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

        targets = [entity for entity in self.nearby_entities if entity != self and entity.hp > 0]
        if targets:
            target = random.choice(targets)
            if target.hp == 1:
                attack = engine.action_manager.get_action(session, self, BeastBite.id)
                attack.target = target
                engine.action_manager.queue_action_instance(attack)
                return
            else:
                evade_action = engine.action_manager.get_action(session, self, BeastEvade.id)
                if target.energy >= 5:
                    # Проверь кулдаун перед добавлением в очередь
                    if session.turn > evade_action.cooldown_turn:
                        engine.action_manager.queue_action(session, self, BeastEvade.id)
                        return

                else:
                    if target.energy == 0:
                        attack = engine.action_manager.get_action(session, self, BeastAttackTwo.id)
                        attack.target = target
                        engine.action_manager.queue_action_instance(attack)
                        return
                    else:
                        attack = engine.action_manager.get_action(session, self, BeastAttack.id)
                        attack.target = target
                        engine.action_manager.queue_action_instance(attack)
                        return
        else:
            # If no valid targets, the beast reloads
            engine.action_manager.queue_action(session, self, BeastReload.id)
            return

        if percentage_chance(5):
            engine.action_manager.queue_action(session, self, BeastReload.id)
            return

        if self.energy == 0:
            engine.action_manager.queue_action(session, self, BeastReload.id)
            return

        if percentage_chance(30):
            engine.action_manager.queue_action(session, self, BeastEvade.id)
            return


@AttachedAction(Beast)
class BeastApproach(DecisiveAction):
    id = 'Beast_approach'
    name = 'Крастца'
    target_type = OwnOnly()

    def func(self, source, target):
        source.nearby_entities = list(filter(lambda t: t != source, self.session.entities))
        for entity in source.nearby_entities:
            if source not in entity.nearby_entities:
                entity.nearby_entities.append(source)
        self.session.say(f'🐾|{source.name} крадётся к своей жертве ближе...')


@AttachedAction(Beast)
class BeastReload(DecisiveAction):
    id = 'Beast_reload'
    name = 'Перевести дух'
    target_type = OwnOnly()

    def func(self, source, target):
        self.session.say(f'😤|{source.name} переводит дух. Энергия восстановлена ({source.max_energy})!')
        source.energy = source.max_energy


@AttachedAction(Beast)
class BeastEvade(DecisiveAction):
    id = 'Beast_evade'
    name = 'Резко отпрыгнуть'
    target_type = OwnOnly()

    def __init__(self, session: Session, source: Entity):
        super().__init__(session, source)
        self.cooldown_turn = 0  # Инициализация кулдауна

    def is_on_cooldown(self) -> bool:
        # Проверка, находится ли действие на кулдауне
        return self.session.turn <= self.cooldown_turn

    def func(self, source, target):
        # Проверка кулдауна
        if self.is_on_cooldown():
            return

        source.inbound_accuracy_bonus = -6
        self.session.say(f'💨|{source.name} резко отпрыгивает назад!')

        # Установка кулдауна на 4 хода от текущего хода
        self.cooldown_turn = self.session.turn + 4

@AttachedAction(Beast)
class BeastGrowl(DecisiveAction):
    id = 'Beast_Growl'
    name = 'Рычать'
    target_type = OwnOnly()

    def func(self, source, target):
        self.session.say(f"💢|{source.name} рычит.")


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
    ATTACK_MESSAGE = "❕|{source_name} атакует когтями {target_name}! Нанесено {damage} урона."
    MISS_MESSAGE = "💨|{source_name} атакует когтями {target_name}, но не попадает."

    id = 'Beast_attack'
    name = 'Царапать когтями'
    target_type = Enemies()


@AttachedAction(BeastWeapon)
class BeastAttackTwo(MeleeAttack):
    id = 'Beast_attack_Two'
    name = 'Кусать клыками'
    target_type = Enemies()

    def func(self, source, target):
        # Вычисляем урон
        lost_hp = target.max_hp - target.hp  # Потерянное здоровье цели
        final_damage = 1 + (3 * lost_hp)  # 1 базовый урон + 3 урона за каждое потерянное ХП

        target.hp = max(0, target.hp - final_damage)  # Применение урона

        # Сообщение о нанесении урона
        self.session.say(f"❕|{source.name} атакует когтями {target.name}. Нанесено {final_damage} урона.")


@AttachedAction(BeastWeapon)
class BeastBite(MeleeAttack):
    id = 'beast_bite'
    name = 'Cтремительный укус'

    def func(self, source, target):
        target.hp = max(0, target.hp - 1)
        self.session.say(f"❕❕|{source.name} делает стремительный прыжок к {target.name} и кусает его! Цель теряет 1♥️.")
