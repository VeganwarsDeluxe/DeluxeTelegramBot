from VegansDeluxe.core import AttachedAction, RegisterWeapon
from VegansDeluxe.core import FreeWeaponAction, MeleeAttack, RegisterEvent, PostTickGameEvent
from VegansDeluxe.core import OwnOnly, EventContext
from VegansDeluxe.core.Translator.LocalizedString import ls
from VegansDeluxe.core.Weapons.Weapon import MeleeWeapon
import random

@RegisterWeapon
class Chainsaw(MeleeWeapon):
    id = 'chainsaw'
    name = ls("weapon_chainsaw_name")
    description = ls("weapon_chainsaw_description")

    cubes = 2
    accuracy_bonus = 2
    energy_cost = 2
    damage_bonus = 0

    def __init__(self, session_id: str, entity_id: str):
        super().__init__(session_id, entity_id)
        self.chainsaw = False
        self.turns_active = 0  # Количество ходов, которые пила активна

@AttachedAction(Chainsaw)
class ChainsawAttack(MeleeAttack):
    def func(self, source, target):
        # Если пила не заведена, урон будет ниже
        if not self.weapon.chainsaw:
            self.weapon.cubes = 2
            self.weapon.damage_bonus = 0
            self.weapon.accuracy_bonus = 2
            self.weapon.energy_cost = 1
        else:
            # 5% шанс, что цепь слетит или пила забьется
            if random.randint(0, 100) < 5:
                self.weapon.chainsaw = False
                self.weapon.turns_active = 0
                self.weapon.cubes = 2
                self.weapon.damage_bonus = 0
                self.weapon.energy_cost = 1
                self.weapon.accuracy_bonus = 2
                self.session.say(ls("weapon_chainsaw_jammed").format(source.name))
                return

        damage = super().func(source, target)
        return damage

@AttachedAction(Chainsaw)
class SwitchChainsaw(FreeWeaponAction):
    id = 'switch_chainsaw'
    target_type = OwnOnly()
    priority = -10

    @property
    def name(self):
        return ls("weapon_chainsaw_enable_name")

    def func(self, source, target):
        if self.weapon.chainsaw:
            self.session.say(ls("weapon_chainsaw_active").format(source.name, self.weapon.turns_active))
            return

        self.weapon.chainsaw = True
        self.weapon.turns_active = 5
        self.weapon.cubes = 3
        self.weapon.damage_bonus = 1
        self.weapon.energy_cost = 2
        self.weapon.accuracy_bonus = 2

        self.session.say(ls("weapon_chainsaw_switch_text").format(source.name, ls("weapon_chainsaw_enable_text")))

@RegisterEvent(Chainsaw.id, event=PostTickGameEvent)
def reduce_turns_active(context: EventContext[PostTickGameEvent]):
    weapon = context.entity.get_weapon_by_id(Chainsaw.id)

    if weapon.chainsaw:
        weapon.turns_active -= 1
        if weapon.turns_active <= 0:
            weapon.chainsaw = False
            weapon.cubes = 2
            weapon.damage_bonus = 0
            weapon.energy_cost = 1
            weapon.accuracy_bonus = 2
            context.session.say(ls("weapon_chainsaw_disable_text").format(context.entity.name))
