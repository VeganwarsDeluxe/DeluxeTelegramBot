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
from game.Matches.DeathMatch import DeathMatch
from game.Matches.GuardianDungeon import GuardianDungeon
from game.Matches.TestGameMatchTeam import TestGameMatchTeam
from game.Matches.TestMatches import Test


r = Router()


@r.message(Command("vd_prepare"))
async def echo_handler(m: Message) -> None:
    flow = MatchCreationFlow(m.chat.id, BaseMatch)
    await flow.execute(m.bot)


@r.message(Command("vd_deathmatch"))
async def echo_handler(m: Message) -> None:
    flow = MatchCreationFlow(m.chat.id, DeathMatch)
    await flow.execute(m.bot)



@r.message(Command("vd_testgame"))
async def echo_handler(m: Message) -> None:
    flow = MatchCreationFlow(m.chat.id, TestGameMatch)
    await flow.execute(m.bot)

@r.message(Command("vd_testgame_team"))
async def echo_handler(m: Message) -> None:
    flow = MatchCreationFlow(m.chat.id, TestGameMatchTeam)
    await flow.execute(m.bot)

@r.message(Command("vd_test"))
async def echo_handler(m: Message) -> None:
    flow = MatchCreationFlow(m.chat.id, Test)
    await flow.execute(m.bot)


@r.message(Command("vd_elemental"))
async def echo_handler(m: Message) -> None:
    flow = MatchCreationFlow(m.chat.id, ElementalDungeon)
    await flow.execute(m.bot)


@r.message(Command("vd_slime"))
async def echo_handler(m: Message) -> None:
    flow = MatchCreationFlow(m.chat.id, SlimeDungeon)
    await flow.execute(m.bot)


@r.message(Command("vd_beast"))
async def echo_handler(m: Message) -> None:
    flow = MatchCreationFlow(m.chat.id, BeastDungeon)
    await flow.execute(m.bot)

@r.message(Command("vd_guardian"))
async def echo_handler(m: Message) -> None:
    flow = MatchCreationFlow(m.chat.id, GuardianDungeon)
    await flow.execute(m.bot)


@r.message(Command("vd_bots"))
async def echo_handler(m: Message) -> None:
    flow = MatchCreationFlow(m.chat.id, BotDungeon)
    await flow.execute(m.bot)
