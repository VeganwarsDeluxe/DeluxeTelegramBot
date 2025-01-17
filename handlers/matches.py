from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from Matches.AndroidMatch import AndroidMatch
from Matches.BaseMatch import BaseMatch
from Matches.BeastDungeon import BeastDungeon
from Matches.BotDungeon import BotDungeon
from Matches.DeathMatch import DeathMatch
from Matches.ElementalDungeon import ElementalDungeon
from Matches.GuardianDungeon import GuardianDungeon
from Matches.NeuroRatMatch import NeuroRatMatch
from Matches.SlimeDungeon import SlimeDungeon
from Matches.TestGameMatch import TestGameMatch
from Matches.TournierMatch import TournierMatch
from db import db
from flow.MatchCreationFlow import MatchCreationFlow

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


@r.message(Command("vd_tournier"))
async def echo_handler(m: Message) -> None:
    flow = MatchCreationFlow(m.chat.id, TournierMatch)
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


@r.message(Command("vd_neurorat"))
async def echo_handler(m: Message) -> None:
    flow = MatchCreationFlow(m.chat.id, NeuroRatMatch)
    code = db.get_user_locale(m.from_user.id)
    await flow.execute(m.bot, code)


@r.message(Command("vd_android"))
async def echo_handler(m: Message) -> None:
    flow = MatchCreationFlow(m.chat.id, AndroidMatch)
    code = db.get_user_locale(m.from_user.id)
    await flow.execute(m.bot, code)

