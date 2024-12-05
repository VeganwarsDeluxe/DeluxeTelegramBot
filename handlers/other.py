import traceback

from VegansDeluxe.core import ls
from aiogram import Router
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import Message
from aiogram.utils.formatting import Text

import config
from db import db
from flow.MatchStartFlow import MatchStartFlow
from startup import mm, engine

r = Router()


@r.message(Command("do"))
async def echo_handler(m: Message) -> None:
    if m.from_user.id not in config.admin_ids:
        return
    if not m.text.count(' '):
        return
    code = m.text.split(' ', 1)[1]
    try:
        result = eval(code)
    except:
        result = traceback.format_exc()
    await m.answer(**Text(f"Code: {code}\n\nResult: {result}").as_kwargs())


@r.message(Command("vd_delete"))
async def echo_handler(m: Message) -> None:
    code = db.get_user_locale(m.from_user.id)

    match = mm.get_match(m.chat.id)
    if not match:
        await m.reply(**Text(ls("bot.delete.game_not_started").localize(code)).as_kwargs())
        return
    del mm.matches[match.id]
    engine.detach_session(match.session)
    await m.reply(**Text(ls("bot.delete.success").localize(code)).as_kwargs())


@r.message(Command("vd_skill_amount"))
async def echo_handler(m: Message) -> None:
    code = db.get_user_locale(m.from_user.id)

    if not m.text.count(' ') == 1:
        return
    skill_amount = m.text.split(' ', 1)[1]
    if not skill_amount.isnumeric():
        return
    skill_amount = int(skill_amount)
    if skill_amount < 0:
        return

    match = mm.get_match(m.chat.id)
    if not match:
        await m.reply(**Text(ls("bot.join.game_not_started").localize(code)).as_kwargs())
        return
    if not match.lobby:
        await m.reply(**Text(ls("bot.join.game_already_started").localize(code)).as_kwargs())
        return

    match.skill_cycles = skill_amount
    await m.bot.send_message(m.chat.id, ls("bot.skill_amount.text").format(skill_amount).localize(code))


@r.message(Command("vd_join"))
async def echo_handler(m: Message) -> None:
    code = db.get_user_locale(m.from_user.id)

    match = mm.get_match(m.chat.id)
    if not match:
        await m.reply(**Text(ls("bot.join.game_not_started").localize(code)).as_kwargs())
        return
    if str(m.from_user.id) in match.player_ids:
        await m.reply(**Text(ls("bot.join.already_joined").localize(code)).as_kwargs())
        return
    if not match.lobby:
        await m.reply(**Text(ls("bot.join.game_already_started").localize(code)).as_kwargs())
        return
    try:
        await m.bot.send_message(m.from_user.id, ls("bot.join.success").localize(code))
    except:
        await m.reply(**Text(ls("bot.join.open_pm").localize(code)).as_kwargs())
        return
    await match.join_session(m.from_user.id, m.from_user.full_name)

    await m.bot.send_message(m.chat.id, ls("bot.join.text").localize(match.locale).format(m.from_user.full_name))


@r.message(CommandStart(deep_link=True))
async def handler(m: Message, command: CommandObject):
    args = command.args
    code = db.get_user_locale(m.from_user.id)
    bot = m.bot

    game_id = int(args.split('_')[-1])
    match = mm.get_match(game_id)

    if not match:
        await m.reply(ls("bot.callback.join.game_not_started").localize(code))
        return
    if str(m.from_user.id) in match.player_ids:
        await m.reply(ls("bot.join.already_joined").localize(code))
        return
    if not match.lobby:
        await m.reply(ls("bot.join.game_already_started").localize(code))
        return
    await match.join_session(m.from_user.id, m.from_user.full_name)

    await bot.send_message(m.from_user.id, ls("bot.join.success").localize(code))
    await bot.send_message(match.chat_id, ls("bot.join.text").localize(match.locale).format(m.from_user.full_name))


@r.message(Command("vd_go"))
async def h(m: Message) -> None:
    code = db.get_user_locale(m.from_user.id)

    msf = MatchStartFlow(m.chat.id, m.from_user.id, mm)
    result = await msf.execute()
    if result:
        await m.reply(**Text(result.localize(code)).as_kwargs())


@r.message(Command("vd_suicide"))
async def h(m: Message) -> None:
    match = mm.get_match(m.chat.id)
    if not match:
        return
    player = match.get_player(m.from_user.id)
    if not player:
        return
    if match.lobby:
        return
    player.dead = True
    player.hp = 0
    if not match.unready_players:
        match.session.say(ls("bot.suicide.text").format(player.name))
        await match.cycle()
