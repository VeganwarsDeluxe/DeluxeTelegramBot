import random
from VegansDeluxe.core import RangedAttack, RegisterWeapon, Entity, Enemies, AttachedAction, At
from VegansDeluxe.core.Events import PostDamageGameEvent, PreActionsGameEvent
from VegansDeluxe.core.Sessions import Session
from VegansDeluxe.core.Translator.LocalizedString import ls
from VegansDeluxe.core.Weapons.Weapon import RangedWeapon
from VegansDeluxe.core import EventContext
from VegansDeluxe.rebuild import KnockedWeapon

@RegisterWeapon
class Boomerang(RangedWeapon):
    id = 'boomerang'
    name = ls("weapon_boomerang_name")
    description = ls("weapon_boomerang_description")

    cubes = 3
    accuracy_bonus = 3
    energy_cost = 3
    damage_bonus = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.return_turn = 0
        self.turns_until_return = 2
        self.is_thrown = False
        self.throw_energy = 0

@AttachedAction(Boomerang)
class BoomerangAttack(RangedAttack):

    def __init__(self, session: Session, source: Entity, weapon: Boomerang):
        super().__init__(session, source, weapon)

    @property
    def hidden(self) -> bool:
        is_hidden = self.session.turn < self.weapon.return_turn + 1
        if is_hidden:
            self.source.current_weapon = self.weapon
        return is_hidden

    def func(self, source: Entity, target: Entity):
        if self.hidden or self.weapon.is_thrown:
            return

        self.attack_boomerang(source, target)

    def attack_boomerang(self, source: Entity, target: Entity):
        if source.energy < self.weapon.energy_cost:
            self.session.say(ls('boomerang_attack_text_miss').format(source.name, target.name))
            return

        self.weapon.throw_energy = source.energy

        total_damage = self.calculate_damage(source, target)
        source.energy = max(source.energy - self.weapon.energy_cost, 0)

        post_damage = self.publish_post_damage_event(source, target, total_damage)
        target.inbound_dmg.add(source, post_damage, self.session.turn)
        source.outbound_dmg.add(target, post_damage, self.session.turn)

        if not total_damage:
            self.session.say(ls('boomerang_attack_text_miss').format(source.name, target.name))
        else:
            self.session.say(ls("boomerang_attack_text").format(source.name, target.name, total_damage))

        self.weapon.is_thrown = True
        self.weapon.return_turn = self.session.turn + self.weapon.turns_until_return
        state = source.get_state(KnockedWeapon.id)
        state.drop_weapon(source)

        @At(self.session.id, turn=self.weapon.return_turn, event=PreActionsGameEvent)
        def handle_boomerang_return(context: EventContext[PreActionsGameEvent]):
            self.return_boomerang(source)

    def return_boomerang(self, source: Entity):
        if self.weapon.throw_energy == 0:
            self.session.say(ls("boomerang_return_text_miss").format(source.name, "the wind"))
            self.weapon.is_thrown = False
            source.current_weapon = self.weapon
            self.weapon.throw_energy = 0
            return

        target_pool = list(self.get_targets(source, Enemies()))
        if not target_pool:
            target_pool = [source]  # Fallback to self-target if no enemies found
        target = random.choice(target_pool)

        original_energy = self.weapon.throw_energy
        current_energy = source.energy
        source.energy = original_energy

        total_damage = self.calculate_damage(source, target)

        post_damage = self.publish_post_damage_event(source, target, total_damage)
        target.inbound_dmg.add(source, post_damage, self.session.turn)
        source.outbound_dmg.add(target, post_damage, self.session.turn)

        source.energy = current_energy

        if not total_damage:
            self.session.say(ls("boomerang_return_text_miss").format(source.name, target.name))
        else:
            self.session.say(ls("boomerang_return_text").format(source.name, target.name, total_damage))

        self.weapon.is_thrown = False
        source.current_weapon = self.weapon

        self.weapon.throw_energy = 0

    def publish_post_damage_event(self, source: Entity, target: Entity, damage: int) -> int:
        message = PostDamageGameEvent(self.session.id, self.session.turn, source, target, damage)
        self.event_manager.publish(message)
        return message.damage
