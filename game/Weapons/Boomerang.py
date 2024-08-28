import random

from VegansDeluxe.core import RangedAttack, RegisterWeapon, Entity, Enemies, AttachedAction
from VegansDeluxe.core.Events import PostDamageGameEvent
from VegansDeluxe.core.Session import Session
from VegansDeluxe.core.Translator.LocalizedString import ls
from VegansDeluxe.core.Weapons.Weapon import RangedWeapon


@RegisterWeapon
class Boomerang(RangedWeapon):
    id = 'boomerang'
    name = ls("weapon_boomerang_name")
    description = ls("weapon_boomerang_description")

    cubes = 3
    accuracy_bonus = 3
    energy_cost = 3
    damage_bonus = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.throw_turn = None
        self.is_thrown = False
        self.turns_until_return = 0


@AttachedAction(Boomerang)
class BoomerangAttack(RangedAttack):
    def __init__(self, session: Session, source: Entity, weapon: Boomerang):
        super().__init__(session, source, weapon)
        self.primary_damage = random.randint(2, 4)
        self.return_damage = random.randint(3, 5)
        self.targets_count = 1

    def func(self, source, target):
        current_turn = self.session.turn

        if self.weapon.is_thrown:
            if current_turn - self.weapon.throw_turn >= self.weapon.turns_until_return:
                # Бумеранг возвращается
                self.return_boomerang(source)
            else:
                # Бумеранг не вернулся
                self.session.say(ls("boomerang_not_available_text").format(source.name))
        else:
            # Бумеранг не был брошен, выполняем бросок
            self.throw_boomerang(source, target)

    def throw_boomerang(self, source, target):
        post_damage = self.publish_post_damage_event(source, target, self.primary_damage)
        target.inbound_dmg.add(source, post_damage, self.session.turn)
        source.outbound_dmg.add(source, post_damage, self.session.turn)

        self.session.say(ls("boomerang_attack_text")
                         .format(source.name, self.primary_damage, target.name))

        self.weapon.is_thrown = True
        self.weapon.throw_turn = self.session.turn
        self.weapon.turns_until_return = 2  # Устанавливаем количество ходов до возврата
        source.current_weapon = None  # Убираем бумеранг из рук

    def return_boomerang(self, source):
        target_pool = list(self.get_targets(source, Enemies()))
        if target_pool:
            target = random.choice(target_pool)
            post_damage = self.publish_post_damage_event(source, target, self.return_damage)
            target.inbound_dmg.add(source, post_damage, self.session.turn)
            source.outbound_dmg.add(source, post_damage, self.session.turn)

            self.session.say(ls("boomerang_return_text")
                             .format(source.name, self.return_damage, target.name))

        self.weapon.is_thrown = False
        self.weapon.throw_turn = None
        self.weapon.turns_until_return = 0
        source.current_weapon = self.weapon  # Возвращаем бумеранг в руки

    def publish_post_damage_event(self, source, target, damage):
        message = PostDamageGameEvent(self.session.id, self.session.turn, source, target, damage)
        self.event_manager.publish(message)
        return message.damage
