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
        index += 1
        tts += f"{index}. {user.username} - {user.rating}\n"

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
    await m.reply(f'Бій: {a.name} ({a.rating}) vs {b.name} ({b.rating}): {a_s} - {b_s}\n\n'
                  f'Результат: \n'
                  f'{a.name} - {r_a}{a_emoji} \n'
                  f'{b.name} - {r_b}{b_emoji}')
    a.rating = int(r_a)
    b.rating = int(r_b)

    db.submit_match_result(a.id, b.id, a_s, b_s)

    db.commit()
