from VegansDeluxe.core.Translator.LocalizedList import LocalizedList
from VegansDeluxe.core.Weapons.Weapon import RangedWeapon
from VegansDeluxe.core import RangedAttack, FreeWeaponAction, RegisterWeapon, Entity, Enemies, OwnOnly, AttachedAction
from VegansDeluxe.core.Translator.LocalizedString import ls
from VegansDeluxe.core.Events import PostDamageGameEvent
from VegansDeluxe.core.Sessions import Session

import random

from VegansDeluxe.rebuild import Aflame


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
        base_damage = self.calculate_damage(source, target)
        source.energy = max(source.energy - self.weapon.energy_cost, 0)

        targets = [target]
        while len(targets) < self.targets_count:
            target_pool = list(filter(lambda t: t not in targets, self.get_targets(source, Enemies())))
            if not target_pool:
                break
            selected_target = random.choice(target_pool)
            targets.append(selected_target)

        for target in targets:
            post_damage = self.publish_post_damage_event(source, target, base_damage)
            target.inbound_dmg.add(source, post_damage, self.session.turn)
            source.outbound_dmg.add(target, post_damage, self.session.turn)

        if not base_damage:
            self.session.say(ls("grenade_grenade_launcher_text_miss").format(source.name, target.name))
        else:
            self.session.say(ls("grenade_grenade_launcher_text").format(source.name, base_damage,
                                                                        LocalizedList([t.name for t in targets])))

    def perform_molotov_attack(self, source, target):
        source.energy = max(source.energy - self.weapon.energy_cost, 0)

        targets = [target]

        while len(targets) < self.targets_count:
            target_pool = list(filter(lambda t: t not in targets, self.get_targets(source, Enemies())))
            if not target_pool:
                break
            selected_target = random.choice(target_pool)
            targets.append(selected_target)

        for t in targets:
            aflame = t.get_state(Aflame.id)
            if aflame:
                aflame.add_flame(self.session, t, source, 1)

                post_damage = self.publish_post_damage_event(source, t, 0)
                t.inbound_dmg.add(source, post_damage, self.session.turn)
                source.outbound_dmg.add(source, post_damage, self.session.turn)

        if targets:
            self.session.say(ls("molotov_grenade_launcher_text")
                             .format(source.name, LocalizedList([t.name for t in targets])))
        else:
            self.session.say(ls('molotov_grenade_launcher_text_miss'))

    def publish_post_damage_event(self, source: Entity, target: Entity, damage: int) -> int:
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
