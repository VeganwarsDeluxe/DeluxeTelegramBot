from VegansDeluxe.core.Weapons.Weapon import MeleeWeapon
from VegansDeluxe.core import MeleeAttack
from VegansDeluxe.core import AttachedAction, RegisterWeapon
from VegansDeluxe.core.Translator.LocalizedString import ls


@RegisterWeapon
class AbyssalBlade(MeleeWeapon):
    id = 'abyssal_blade'
    name = ls('weapon_abyssal_blade_name')
    description = ls('weapon_abyssal_blade_description')

    cubes = 3
    accuracy_bonus = 2
    energy_cost = 2
    damage_bonus = 0


@AttachedAction(AbyssalBlade)
class AbyssalBladeAttack(MeleeAttack):
    def func(self, source, target):
        damage = super().attack(source, target)
        if not damage:
            return damage
        emptiness = target.get_state('emptiness')
        if emptiness.active:
            emptiness.emptiness -= 1
            self.session.say(ls("weapon_abyssal_blade_increase"))
        else:
            self.session.say(ls("weapon_abyssal_blade_effect").format(target.name))
        emptiness.active = True
        return damage
