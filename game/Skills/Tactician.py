from VegansDeluxe.core import StateContext, EventContext, percentage_chance
from VegansDeluxe.core import RegisterState, RegisterEvent, At
from VegansDeluxe.core import AttackGameEvent
from VegansDeluxe.core import Session
from VegansDeluxe.core.Skills.Skill import Skill
from VegansDeluxe.core.Translator.LocalizedString import ls

class Tactician(Skill):
    id = 'tactician'
    name = ls("skill_tactician_name")
    description = ls("skill_tactician_description")

    def __init__(self):
        super().__init__()

@RegisterState(Tactician)
def register(root_context: StateContext[Tactician]):
    session: Session = root_context.session
    source = root_context.entity

    @RegisterEvent(session.id, event=AttackGameEvent, priority=-10)
    def func(context: EventContext[AttackGameEvent]):
        if context.event.source != source:
            return

        if percentage_chance(25):
            session.say(ls("skill_tactician_effect_text").format(source.name))
            weapon = context.event.source.weapon if context.event.source else None
            if weapon:
                original_energy_cost = weapon.energy_cost
                weapon.energy_cost = 0
                @At(session.id, turn=session.turn + 1, event=AttackGameEvent)
                def reset_energy_cost(context: EventContext[AttackGameEvent]):
                    if context.event.source == source:
                        weapon = context.event.source.weapon if context.event.source else None
                        if weapon:
                            weapon.energy_cost = original_energy_cost
