from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from flow.MatchCreationFlow import MatchCreationFlow
from game.Matches.BaseMatch import BaseMatch
from game.Matches.BeastDungeon import BeastDungeon
from game.Matches.BotDungeon import BotDungeon
from game.Matches.ElementalDungeon import ElementalDungeon
from game.Matches.SlimeDungeon import SlimeDungeon
from game.Matches.TestGameMatch import TestGameMatch

r = Router()


@r.message(Command("vd_prepare"))
async def echo_handler(m: Message) -> None:
    flow = MatchCreationFlow(m.chat.id, BaseMatch)
    flow.execute()


@r.message(Command("vd_testgame"))
async def echo_handler(m: Message) -> None:
    flow = MatchCreationFlow(m.chat.id, TestGameMatch)
    flow.execute()


@r.message(Command("vd_elemental"))
async def echo_handler(m: Message) -> None:
    flow = MatchCreationFlow(m.chat.id, ElementalDungeon)
    flow.execute()


@r.message(Command("vd_slime"))
async def echo_handler(m: Message) -> None:
    flow = MatchCreationFlow(m.chat.id, SlimeDungeon)
    flow.execute()


@r.message(Command("vd_beast"))
async def echo_handler(m: Message) -> None:
    flow = MatchCreationFlow(m.chat.id, BeastDungeon)
    flow.execute()


@r.message(Command("vd_bots"))
async def echo_handler(m: Message) -> None:
    flow = MatchCreationFlow(m.chat.id, BotDungeon)
    flow.execute()
