from datetime import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.formatting import Text

import config
from db import db
from db.Rating import outcome

r = Router()


@r.message(Command("top"))
async def profile_handler(m: Message) -> None:
    tts = ''

    top = db.get_top_players_by_rating(15)
    index = 0
    for user in top:
        if not db.is_player_in_results(user.id):
            continue
        index += 1
        tts += f"{index}. {user.username} - {user.rating}\n"

    await m.answer(**Text(tts).as_kwargs())


@r.message(Command("revert"))
async def h(m: Message) -> None:
    if m.from_user.id not in config.admin_ids:
        return
    if m.text.count(' ') != 1:
        return
    _, datestamp = m.text.split(' ')
    datestamp = int(datestamp)
    db.delete_match_result_by_date(datestamp)
    await m.answer("Done. You may want to /recompile.")


@r.message(Command("recompile"))
async def h(m: Message) -> None:
    if m.from_user.id not in config.admin_ids:
        return
    db.erase_ratings()

    top = db.get_match_results()
    for match in top:
        a = db.get_user(match.opponent_a_id)
        b = db.get_user(match.opponent_b_id)

        r_a, r_b = outcome(a, b, match.opponent_a_score, match.opponent_b_score)
        a.rating = r_a
        b.rating = r_b
        db.commit()
    await m.answer("Recompiled.")


@r.message(Command("matches"))
async def profile_handler(m: Message) -> None:
    tts = ''

    top = db.get_match_results()
    index = 0
    for match in top:
        a = db.get_user(match.opponent_a_id)
        b = db.get_user(match.opponent_b_id)

        date = datetime.fromtimestamp(match.date).strftime('%d.%m.%Y')

        index += 1
        tts += f"{index}. {a.username} vs {b.username}\n"
        tts += f"{match.opponent_a_score}:{match.opponent_b_score}\n"
        tts += f"[{match.date}] ({date})\n\n"

    await m.answer(**Text(tts).as_kwargs())


@r.message(Command("bk"))
async def h(m: Message) -> None:
    if m.text.count(' ') != 2:
        return
    _, a, b = m.text.split(' ')
    a, b = db.get_user_by_username(a), db.get_user_by_username(b)
    if not (a and b):
        await m.reply('Ні!!!')
        return
    EWP_a = 1 / (1 + (10 ** ((b.rating - a.rating) / 400)))
    EWP_b = 1 / (1 + (10 ** ((a.rating - b.rating) / 400)))
    C_a = round(1 / EWP_a, 2) - 1
    C_b = round(1 / EWP_b, 2) - 1
    await m.reply(f'{a.name} {C_a} | {C_b} {b.name}')


@r.message(Command("predict"))
async def h(m: Message) -> None:
    if m.text.count(' ') != 4:
        return
    _, a, b, a_s, b_s = m.text.split(' ')
    a_s, b_s = int(a_s), int(b_s)
    a, b = db.get_user_by_username(a), db.get_user_by_username(b)
    if not (a and b):
        await m.reply('Ні!!!')
        return
    r_a, r_b = outcome(a, b, a_s, b_s)
    a_emoji = '📈' if r_a > a.rating else '📉'
    b_emoji = '📈' if r_b > b.rating else '📉'
    await m.reply(f'ПРОГНОЗ:\n\nБій: {a.name} ({a.rating}) vs {b.name} ({b.rating}): {a_s} - {b_s}\n\n'
                  f'Результат: \n'
                  f'{a.name} - {r_a}{a_emoji} \n'
                  f'{b.name} - {r_b}{b_emoji}')


@r.message(Command("vs"))
async def h(m: Message) -> None:
    if m.from_user.id not in config.admin_ids:
        return
    if m.text.count(' ') != 4:
        return
    _, a, b, a_s, b_s = m.text.split(' ')
    a_s, b_s = int(a_s), int(b_s)
    a, b = db.get_user_by_username(a), db.get_user_by_username(b)
    if not (a and b):
        await m.reply('Ні!!!')
        return
    r_a, r_b = outcome(a, b, a_s, b_s)
    a_emoji = '📈' if r_a > a.rating else '📉'
    b_emoji = '📈' if r_b > b.rating else '📉'

    result, dt = db.submit_match_result(a.id, b.id, a_s, b_s)

    await m.reply(f'Бій: {a.name} ({a.rating}) vs {b.name} ({b.rating}): {a_s} - {b_s}\n\n'
                  f'Результат: \n'
                  f'{a.name} - {r_a}{a_emoji} \n'
                  f'{b.name} - {r_b}{b_emoji}\n\nR-ID: {dt}')

    a.rating = int(r_a)
    b.rating = int(r_b)
    db.commit()
