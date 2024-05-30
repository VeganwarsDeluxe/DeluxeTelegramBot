from VegansDeluxe.core import AttachedAction, RegisterWeapon
from VegansDeluxe.core import MeleeAttack
from VegansDeluxe.core import Entity
from VegansDeluxe.core import Session
from VegansDeluxe.core.Translator.LocalizedString import ls
from VegansDeluxe.core.Weapons.Weapon import MeleeWeapon


@RegisterWeapon
class Lance(MeleeWeapon):
    id = 'lance'
    name = ls("weapon_lance_name")
    description = ls("weapon_lance_description")

    cubes = 3
    accuracy_bonus = 1
    energy_cost = 2
    damage_bonus = 0


@AttachedAction(Lance)
class LanceAttack(MeleeWeapon):
    pass
    #def calculate_damage(self, source, target):
    #    damage = super().calculate_damage(source, target)
    #    if damage == 0:
    #        return 0
    #    damage += 1 if target in source.ranged else 0
    #    return damage

