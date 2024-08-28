from VegansDeluxe.core import MeleeAttack
import random

from VegansDeluxe.core import AttachedAction, RegisterWeapon
from VegansDeluxe.core.Translator.LocalizedString import ls
from VegansDeluxe.core.Weapons.Weapon import MeleeWeapon

from game.States.Weakness import Weakness


@RegisterWeapon
class CursedSword(MeleeWeapon):
    id = 'cursed_sword'
    name = ls("weapon_cursed_sword_name")
    description = ls("weapon_cursed_sword_description")

    accuracy_bonus = 2
    cubes = 3


@AttachedAction(CursedSword)
class CursedSwordAttack(MeleeAttack):
    def func(self, source, target):
        damage = super().attack(source, target).dealt
        if not damage:
            return damage

        if random.randint(0, 100) > 99:
            return damage

        weakness = target.get_state(Weakness.id)

        if weakness.active:
            weakness.weakness += 2
            weakness.triggered = True  # Set triggered to True when mutilation increases
            self.session.say(ls("weapon_cursed_sword_increase"))
        else:
            weakness.active = True
            weakness.triggered = True  # Set triggered to True when mutilation activates
            self.session.say(ls("weapon_cursed_sword_effect").format(target.name))

        return damage
