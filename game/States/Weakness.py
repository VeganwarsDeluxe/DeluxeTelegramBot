from VegansDeluxe.core.Actions.StateAction import DecisiveStateAction
from VegansDeluxe.core import AttachedAction
from VegansDeluxe.core import RegisterState, RegisterEvent
from VegansDeluxe.core import StateContext, EventContext
from VegansDeluxe.core import Entity
from VegansDeluxe.core import PostUpdatesGameEvent, PostDamagesGameEvent
from VegansDeluxe.core import Session
from VegansDeluxe.core import State
from VegansDeluxe.core.Translator.LocalizedString import ls


class Weakness(State):
    id = 'weakness'

    def __init__(self):
        super().__init__()
        self.weakness = 0


@RegisterState(Weakness)
def register(root_context: StateContext[Weakness]):
    session: Session = root_context.session
    source = root_context.entity
    state = root_context.state

    @RegisterEvent(session.id, event=PostUpdatesGameEvent)
    def func(context: EventContext[PostUpdatesGameEvent]):
        if not state.weakness:
            return
        for action in context.action_manager.get_actions(session, source):
            if action.id != 'lay_weakness':
                action.energy_cost += 1

    @RegisterEvent(session.id, event=PostDamagesGameEvent)
    def func(context: EventContext[PostDamagesGameEvent]):
        if not state.weakness:
            return
        if state.weakness == 1:
            session.say(ls("state_recovery_from_weakness").format(source.name))
        state.weakness -= 1

