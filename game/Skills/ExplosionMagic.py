from VegansDeluxe.core import StateContext, EventContext
from VegansDeluxe.core import RegisterEvent, RegisterState, Next
from VegansDeluxe.core import AttachedAction
from VegansDeluxe.core import ItemAction
from VegansDeluxe.core.Actions.StateAction import DecisiveStateAction
from VegansDeluxe.core import Entity

from VegansDeluxe.core import PreActionsGameEvent, DeliveryRequestEvent, DeliveryPackageEvent
from VegansDeluxe.core import Session,PostUpdatesGameEvent
from VegansDeluxe.core.Skills.Skill import Skill
from VegansDeluxe.core import Enemies
from VegansDeluxe.core.Translator.LocalizedString import ls
from VegansDeluxe.core.Actions.WeaponAction import DamageData

import random

class ExplosionMagic(Skill):
    id = 'explosion_magic'
    name = ls("skill_explosion_magic_name")
    description = ls("skill_explosion_magic_description")

    def __init__(self):
        super().__init__()
        self.cooldown_turn = 0
        self.trigger_turn = 0
        self.preparation_texts = [
            ls("skill_explosion_delay_text_1"),
            ls("skill_explosion_delay_text_2"),
            ls("skill_explosion_delay_text_3"),
            ls("skill_explosion_delay_text_4"),
        ]

@RegisterState(ExplosionMagic)
def register(root_context: StateContext[ExplosionMagic]):
    session: Session = root_context.session
    source = root_context.entity

@AttachedAction(ExplosionMagic)
class Explosion(DecisiveStateAction):
    id = 'explosion'
    name = ls("skill_explosion_action_name")
    priority = 0
    target_type = Enemies()

    def __init__(self, session: Session, source: Entity, skill: ExplosionMagic):
        super().__init__(session, source, skill)
        self.state = skill

    @property
    def hidden(self) -> bool:
        return self.session.turn < self.state.cooldown_turn

    def func(self, source: Entity, target: Entity):
        if source.energy < 5:
            self.session.say(ls("not_enough_energy").format(source.name))
            return

        if self.hidden:
            self.session.say(ls("skill_explosion_on_cooldown").format(source.name))
            return

        if self.state.trigger_turn == 0:
            self.state.trigger_turn = self.session.turn + 1

            self.session.say(ls("skill_explosion_staff_text").format(source.name, target.name))
            random_text = random.choice(self.state.preparation_texts)
            self.session.say(random_text.format(source.name))

        elif self.session.turn == self.state.trigger_turn:
            # Наносим фиксированный урон
            self.apply_damage(source, target, 10)

            aflame = target.get_state('aflame')
            aflame.add_flame(self.session, target, source, 6)

            # Применение состояния 'stun' к источнику
            stun_state = source.get_state('stun')
            if not stun_state:
                source.attach_state('stun', 1)
                self.session.say(ls("skill_explosion_stun_text").format(source.name))
            else:
                if stun_state.stun == 0:
                    stun_state.stun = 3
                    self.session.say(ls("skill_explosion_stun_text").format(source.name))
                else:
                    self.session.say(ls("skill_explosion_already_stunned").format(source.name))

            source.energy -= 10
            self.state.cooldown_turn = self.session.turn + 12
            self.state.trigger_turn = 0
            self.session.say(ls("skill_explosion_text").format(source.name))
            self.session.say(ls("skill_explosion_effect_text").format(target.name, 10, source.name))

    def apply_damage(self, source: Entity, target: Entity, damage: int):
        damage_data = DamageData(damage, damage, damage)
        target.inbound_dmg.add(source, damage, self.session.turn)
        source.outbound_dmg.add(target, damage, self.session.turn)
