from VegansDeluxe.core import ls

from game.Entities.TelegramEntity import TelegramEntity
from game.Matches.BaseMatch import BaseMatch


class TeamMatch(BaseMatch):
    name = ls("matches.teams")

    def __init__(self, chat_id, bot):
        super().__init__(chat_id, bot)

    def get_players_in_team(self, team=None) -> list[TelegramEntity]:
        return [player for player in self.session.entities if player.team == team]

    def join_team(self, player, team=None):
        player.team = team

    def delete_team(self, team):
        for player in self.get_players_in_team(team):
            player.team = None

    def create_team(self, player):
        player.team = player.id
