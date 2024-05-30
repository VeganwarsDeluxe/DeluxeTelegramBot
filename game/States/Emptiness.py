from VegansDeluxe.core import RegisterState, RegisterEvent
from VegansDeluxe.core import StateContext, EventContext
from VegansDeluxe.core import PreDamagesGameEvent
from VegansDeluxe.core import Session
from VegansDeluxe.core import State
from VegansDeluxe.core.Translator.LocalizedString import ls


class Emptiness(State):
    id = 'emptiness'

    def __init__(self):
        super().__init__()
        self.emptiness = 3
        self.active = False


@RegisterState(Emptiness)
def register(root_context: StateContext[Emptiness]):
    session: Session = root_context.session
    source = root_context.entity
    state = root_context.state

    @RegisterEvent(session.id, event=PreDamagesGameEvent, filters=[lambda e: state.active])
    def func(context: EventContext[PreDamagesGameEvent]):
        if state.emptiness <= 0:
            session.say(ls("state_emptiness_energy_loss").format(source.name, source.max_energy - 1))
            source.max_energy -= 1
            state.active = False
            state.emptiness = 3
            return
        session.say(ls("state_emptiness_timer").format(source.name, max(state.emptiness, 0)))
        state.emptiness -= 1
