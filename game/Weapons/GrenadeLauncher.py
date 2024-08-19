from VegansDeluxe.core.Translator.LocalizedList import LocalizedList
from VegansDeluxe.core.Weapons.Weapon import RangedWeapon
from VegansDeluxe.core import RangedAttack, FreeWeaponAction, RegisterWeapon, Entity, Enemies, OwnOnly, AttachedAction
from VegansDeluxe.core.Translator.LocalizedString import ls
from VegansDeluxe.core.Events import PostDamageGameEvent
from VegansDeluxe.core.Sessions import Session

import random


@RegisterWeapon
class GrenadeLauncher(RangedWeapon):
    id = 'grenade_launcher'
    name = ls("weapon_grenade_launcher_name")
    description = ls("weapon_grenade_launcher_description")

    cubes = 4
    accuracy_bonus = 2
    energy_cost = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_molotov = False  # Начальный режим - гранаты


@AttachedAction(GrenadeLauncher)
class GrenadeLauncherAttack(RangedAttack):
    def __init__(self, session: Session, source: Entity, weapon: GrenadeLauncher):
        super().__init__(session, source, weapon)
        self.targets_count = 2

    def func(self, source, target):
        if self.weapon.is_molotov:
            self.perform_molotov_attack(source, target)
        else:
            self.perform_grenade_attack(source, target)

    def perform_grenade_attack(self, source, target):
        damage = random.randint(1, self.weapon.cubes)
        targets = []
        for _ in range(self.targets_count):
            target_pool = list(filter(lambda t: t not in targets, self.get_targets(source, Enemies())))
            if not target_pool:
                continue
            selected_target = random.choice(target_pool)
            post_damage = self.publish_post_damage_event(source, selected_target, damage)
            selected_target.inbound_dmg.add(source, post_damage, self.session.turn)
            source.outbound_dmg.add(source, post_damage, self.session.turn)
            targets.append(selected_target)

        self.session.say(ls("grenade_grenade_launcher_text")
                         .format(source.name, damage, LocalizedList([t.name for t in targets])))

    def perform_molotov_attack(self, source, target):
        targets = []
        for _ in range(self.targets_count):
            target_pool = list(filter(lambda t: t not in targets, self.get_targets(source, Enemies())))
            if not target_pool:
                continue
            selected_target = random.choice(target_pool)
            self.apply_molotov_effect(source, selected_target)
            targets.append(selected_target)

        source.energy = max(source.energy - self.weapon.energy_cost, 0)
        self.session.say(ls("molotov_grenade_launcher_text")
                         .format(source.name, LocalizedList([t.name for t in targets])))

    def apply_molotov_effect(self, source, target):
        aflame = target.get_state('aflame')
        aflame.add_flame(self.session, target, source, 1)
        post_damage = self.publish_post_damage_event(source, target, 0)
        target.inbound_dmg.add(source, post_damage, self.session.turn)
        source.outbound_dmg.add(source, post_damage, self.session.turn)

    def publish_post_damage_event(self, source, target, damage):
        message = PostDamageGameEvent(self.session.id, self.session.turn, source, target, damage)
        self.event_manager.publish(message)
        return message.damage


@AttachedAction(GrenadeLauncher)
class SwitchGrenadeLauncher(FreeWeaponAction):
    id = 'switch_grenade_launcher'
    target_type = OwnOnly()
    priority = -10

    @property
    def name(self):
        return ls("switch_to_grenade_launcher") if self.weapon.is_molotov else ls("switch_to_molotov_launcher")

    def func(self, source, target):
        self.weapon.is_molotov = not self.weapon.is_molotov
        if self.weapon.is_molotov:
            self.session.say(ls("switch_to_molotov_text").format(source.name))
        else:
            self.session.say(ls("switch_to_grenade_text").format(source.name))
