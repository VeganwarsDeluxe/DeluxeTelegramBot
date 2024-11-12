from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from db import db
from flow.MatchCreationFlow import MatchCreationFlow
from game.Matches.BaseMatch import BaseMatch
from game.Matches.BeastDungeon import BeastDungeon
from game.Matches.BotDungeon import BotDungeon
from game.Matches.DeathMatch import DeathMatch
from game.Matches.ElementalDungeon import ElementalDungeon
from game.Matches.GuardianDungeon import GuardianDungeon
from game.Matches.SlimeDungeon import SlimeDungeon
from game.Matches.TestGameMatch import TestGameMatch
from game.Matches.TestGameMatchTeam import TestGameMatchTeam

r = Router()


@r.message(Command("vd_prepare"))
async def echo_handler(m: Message) -> None:
    flow = MatchCreationFlow(m.chat.id, BaseMatch)
    code = db.get_user_locale(m.from_user.id)
    await flow.execute(m.bot, code)


@r.message(Command("vd_deathmatch"))
async def echo_handler(m: Message) -> None:
    flow = MatchCreationFlow(m.chat.id, DeathMatch)
    code = db.get_user_locale(m.from_user.id)
    await flow.execute(m.bot, code)


@r.message(Command("vd_testgame"))
async def echo_handler(m: Message) -> None:
    flow = MatchCreationFlow(m.chat.id, TestGameMatch)
    code = db.get_user_locale(m.from_user.id)
    await flow.execute(m.bot, code)


@r.message(Command("vd_testgame_team"))
async def echo_handler(m: Message) -> None:
    flow = MatchCreationFlow(m.chat.id, TestGameMatchTeam)
    code = db.get_user_locale(m.from_user.id)
    await flow.execute(m.bot, code)


@r.message(Command("vd_elemental"))
async def echo_handler(m: Message) -> None:
    flow = MatchCreationFlow(m.chat.id, ElementalDungeon)
    code = db.get_user_locale(m.from_user.id)
    await flow.execute(m.bot, code)


@r.message(Command("vd_slime"))
async def echo_handler(m: Message) -> None:
    flow = MatchCreationFlow(m.chat.id, SlimeDungeon)
    code = db.get_user_locale(m.from_user.id)
    await flow.execute(m.bot, code)


@r.message(Command("vd_beast"))
async def echo_handler(m: Message) -> None:
    flow = MatchCreationFlow(m.chat.id, BeastDungeon)
    code = db.get_user_locale(m.from_user.id)
    await flow.execute(m.bot, code)


@r.message(Command("vd_guardian"))
async def echo_handler(m: Message) -> None:
    flow = MatchCreationFlow(m.chat.id, GuardianDungeon)
    code = db.get_user_locale(m.from_user.id)
    await flow.execute(m.bot, code)


@r.message(Command("vd_bots"))
async def echo_handler(m: Message) -> None:
    flow = MatchCreationFlow(m.chat.id, BotDungeon)
    code = db.get_user_locale(m.from_user.id)
    await flow.execute(m.bot, code)
