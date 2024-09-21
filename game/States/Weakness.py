from VegansDeluxe.core import StateContext, EventContext, percentage_chance
from VegansDeluxe.core import RegisterState, RegisterEvent, At
from VegansDeluxe.core import PreDamagesGameEvent, PostUpdatesGameEvent, PostDamagesGameEvent
from VegansDeluxe.core import Session, Entity
from VegansDeluxe.core.States import State
from VegansDeluxe.core.Translator.LocalizedString import ls

from VegansDeluxe.core.Actions.StateAction import DecisiveStateAction
from VegansDeluxe.core import AttachedAction

class Weakness(State):
    id = 'weakness'

    def __init__(self):
        super().__init__()
        self.weakness = 0
        self.triggered = False

@RegisterState(Weakness)
def register(root_context: StateContext[Weakness]):
    session: Session = root_context.session
    source = root_context.entity
    state = root_context.state
    target = root_context.entity

    @RegisterEvent(session.id, event=PreDamagesGameEvent)
    def func_damage(context: EventContext[PreDamagesGameEvent]):
        if state.weakness > 0 and not state.triggered:
            if target.weapon:
                session.say(ls("state_weakness_energy_cost_increase").format(target.name, target.weapon.energy_cost + 1))
                target.weapon.energy_cost += 1
                state.weakness += 1
                state.triggered = True

    @RegisterEvent(session.id, event=PostUpdatesGameEvent)
    def func_reset(context: EventContext[PostUpdatesGameEvent]):
        if state.weakness == 1:
            if target.weapon:
                session.say(ls("state_recovery_from_weakness").format(source.name))
                if state.triggered:
                    target.weapon.energy_cost -= 1

                state.triggered = False

            state.weakness -= 1


