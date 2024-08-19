from VegansDeluxe.core import AttachedAction, RegisterWeapon
from VegansDeluxe.core import RangedAttack
from VegansDeluxe.core import EventContext
from VegansDeluxe.core import PostTickGameEvent
from VegansDeluxe.core.Translator.LocalizedString import ls
from VegansDeluxe.core.Weapons.Weapon import RangedWeapon
from game.States.Hunger import Hunger

import random

@RegisterWeapon
class Emitter(RangedWeapon):
    id = 'emitter'
    name = ls("weapon_emitter_name")
    description = ls("weapon_emitter_description")

    cubes = 2
    accuracy_bonus = 2
    energy_cost = 3
    damage_bonus = 0

@AttachedAction(Emitter)
class EmitterAttack(RangedAttack):
    def func(self, source, target):
        damage = super().attack(source, target)
        if not damage:
            return damage

        if random.randint(0, 100) <= 99:  # 20% шанс, 99 для тестов
            hunger = target.get_state('hunger')
            if hunger is None:
                hunger = Hunger()
                event_manager = self.session.event_manager
                target.attach_state(hunger, event_manager)

            hunger.hunger += 1
            self.session.say(ls("weapon_emitter_effect").format(target.name, hunger.hunger))


        return damage


