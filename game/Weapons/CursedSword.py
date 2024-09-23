from VegansDeluxe.core import AttachedAction, RegisterWeapon, percentage_chance
from VegansDeluxe.core import MeleeAttack
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
    async def func(self, source, target):
        attack = await super().attack(source, target)
        damage = attack.dealt
        if not damage:
            return damage

        # 99% chance to apply the weakness effect
        if percentage_chance(99):
            weakness = target.get_state(Weakness.id)

            self.session.say(ls("weapon_cursed_sword_effect").format(target.name))
            weakness.weakness += 2  # Increase the weakness stack
            weakness.active = True  # Activate the weakness effect

        return damage
