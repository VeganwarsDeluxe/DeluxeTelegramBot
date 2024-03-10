from flow.MatchCreationFlow import MatchCreationFlow
from game.Matches.BaseMatch import BaseMatch
from game.Matches.ElementalDungeon import ElementalDungeon
from game.Matches.Matchmaker import Matchmaker
from game.Matches.SlimeDungeon import SlimeDungeon
from game.Matches.TestGameMatch import TestGameMatch
from handlers.bot import ExtendedBot


def initialize_module(bot: ExtendedBot, mm: Matchmaker):
    @bot.message_handler(commands=['vd_prepare'])
    def vd_prepare_handler(m):
        flow = MatchCreationFlow(m.chat.id, mm, BaseMatch)
        flow.execute()

    @bot.message_handler(commands=['vd_testgame'])
    def vd_prepare_handler(m):
        flow = MatchCreationFlow(m.chat.id, mm, TestGameMatch)
        flow.execute()

    @bot.message_handler(commands=['vd_elemental'])
    def vd_prepare_handler(m):
        flow = MatchCreationFlow(m.chat.id, mm, ElementalDungeon)
        flow.execute()

    @bot.message_handler(commands=['vd_slime'])
    def vd_prepare_handler(m):
        flow = MatchCreationFlow(m.chat.id, mm, SlimeDungeon)
        flow.execute()
