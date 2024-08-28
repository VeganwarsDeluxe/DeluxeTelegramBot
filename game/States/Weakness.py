from VegansDeluxe.core.Actions.StateAction import DecisiveStateAction
from VegansDeluxe.core import AttachedAction
from VegansDeluxe.core import RegisterState, RegisterEvent
from VegansDeluxe.core import StateContext, EventContext
from VegansDeluxe.core import Entity
from VegansDeluxe.core import PostUpdatesGameEvent, PostDamagesGameEvent, PreDamagesGameEvent, At
from VegansDeluxe.core import Session
from VegansDeluxe.core import State
from VegansDeluxe.core.Translator.LocalizedString import ls


from VegansDeluxe.core import RegisterState, RegisterEvent, StateContext, EventContext, Session
from VegansDeluxe.core import PreDamagesGameEvent, PostDamagesGameEvent
from VegansDeluxe.core.Translator.LocalizedString import ls

class Weakness(State):
    id = 'weakness'

    def __init__(self):
        super().__init__()
        self.weakness = 0  # Initialize weakness stack
        self.active = False
        self.triggered = False

@RegisterState(Weakness)
def register(root_context: StateContext[Weakness]):
    session: Session = root_context.session
    target = root_context.entity
    state = root_context.state

    @RegisterEvent(session.id, event=PreDamagesGameEvent, filters=[lambda e: state.active])
    def func_damage(context: EventContext[PreDamagesGameEvent]):
        if state.weakness >= 1:
            if target.weapon:
                session.say(ls("state_weakness_energy_cost_increase").format(target.name, target.weapon.energy_cost + 1))
                target.weapon.energy_cost += 1
            state.active = False  # End effect after application
            state.weakness = 1  # Ensure the stack remains at 1

            # Schedule a delayed event to handle the reset of energy cost
            @At(session.id, turn=session.turn + 1, event=PostUpdatesGameEvent)
            def func_reset(context: EventContext[PostUpdatesGameEvent]):
                if state.weakness:
                    if target.weapon:
                        session.say(ls("state_recovery_from_weakness").format(target.name))
                        target.weapon.energy_cost -= 1
                    state.weakness -= 1
                    if state.weakness <= 0:
                        state.active = False

    state.triggered = False