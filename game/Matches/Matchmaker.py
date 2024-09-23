# TODO: Refactor


class Matchmaker:
    """Matchmaker Class: Handles matches.."""

    def __init__(self, engine):
        """Initialization function."""
        self.engine = engine

        self.action_manager = self.engine.action_manager
        self.session_manager = self.engine.session_manager
        self.event_manager = self.engine.event_manager

        self.matches = {}

    def attach_match(self, match):
        self.matches.update({match.id: match})

    def get_match(self, chat_id):
        match = self.matches.get(str(chat_id))
        if not match:
            return
        if not match.session.active:
            del self.matches[match.id]
            return
        return match
