from VegansDeluxe.core.Weapons.Weapon import RangedWeapon
from VegansDeluxe.core import RangedAttack, RegisterWeapon, Entity, AttachedAction, OwnOnly, DecisiveStateAction, \
    FreeWeaponAction, Enemies
from VegansDeluxe.core.Session import Session
from VegansDeluxe.core.Translator.LocalizedString import ls
from VegansDeluxe.core.Weapons.Weapon import RangedWeapon


@RegisterWeapon
class Shurikens(RangedWeapon):
    id = 'shurikens'
    name = ls("weapon_shurikens_name")
    description = ls("weapon_shurikens_description")

    cubes = 1
    accuracy_bonus = 2
    energy_cost = 2
    damage_bonus = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.double_shuriken = False
        self.ammo = 4


@AttachedAction(Shurikens)
class ShurikenAttack(RangedAttack):
    id = 'shuriken_attack'
    target_type = Enemies()

    def __init__(self, session: Session, source: Entity, weapon: Shurikens):
        super().__init__(session, source, weapon)

        source.energy = max(source.energy - self.weapon.energy_cost, 0)

    def func(self, source, target):
        if self.weapon.ammo > 0:
            if self.weapon.double_shuriken and self.weapon.ammo >= 2:
                self.perform_double_shuriken_attack(source, target)
            else:
                self.perform_single_shuriken_attack(source, target)
        else:
            self.session.say(ls("shuriken_no_ammo_text").format(source.name))

    def perform_single_shuriken_attack(self, source, target):
        post_damage = self.publish_post_attack_event(source, target)
        target.inbound_dmg.add(source, post_damage, self.session.turn)
        source.outbound_dmg.add(source, post_damage, self.session.turn)

        self.session.say(ls("weapon_shuriken_throw_name").format(source.name, post_damage, target.name))
        self.weapon.ammo -= 1

    def perform_double_shuriken_attack(self, source, target):
        # Первый бросок сюрикена
        post_damage1 = self.publish_post_attack_event(source, target)
        target.inbound_dmg.add(source, post_damage1, self.session.turn)
        source.outbound_dmg.add(source, post_damage1, self.session.turn)

        # Второй бросок сюрикена
        post_damage2 = self.publish_post_attack_event(source, target)
        target.inbound_dmg.add(source, post_damage2, self.session.turn)
        source.outbound_dmg.add(source, post_damage2, self.session.turn)

        # Сообщение о двойной атаке
        self.session.say(ls("weapon_double_shuriken_throw_name")
                         .format(source.name, post_damage1, target.name, post_damage2, target.name))
        self.weapon.ammo -= 2


@AttachedAction(Shurikens)
class SwitchShurikenMode(FreeWeaponAction):
    id = 'switch_shuriken_mode'
    target_type = OwnOnly()
    priority = -10

    @property
    def name(self):
        return ls("switch_shuriken_mode") if not self.weapon.double_shuriken else ls("switch_shuriken_mode")

    def func(self, source, target):
        self.weapon.double_shuriken = not self.weapon.double_shuriken
        if self.weapon.double_shuriken:
            self.session.say(ls("switch_to_double_shuriken_text").format(source.name))
        else:
            self.session.say(ls("switch_to_single_shuriken_text").format(source.name))


@AttachedAction(Shurikens)
class PickUpShuriken(DecisiveStateAction):
    id = 'pick_up'
    name = "shuriken_pickup_name"
    target_type = OwnOnly()

    # Ну шо це за жесть. Shurikens це зброя а не скілл/стейт, ну куди DecisiveStateAction.......
    # Виправляйте....
    def __init__(self, session: Session, source: Entity, skill: Shurikens):
        super().__init__(session, source, skill)
        self.weapon = skill

    @property
    def hidden(self) -> bool:
        return self.weapon.ammo == 4

    def func(self, source, target):
        self.weapon.ammo = 4
        self.session.say(ls("shuriken_pickup_text").format(source.name))
