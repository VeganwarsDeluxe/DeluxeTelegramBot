from VegansDeluxe.core import ls
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.formatting import Text

import config
from db import db
from handlers.callbacks.other import ChangeLocale
from startup import translator

r = Router()


@r.message(Command("profile"))
async def profile_handler(m: Message) -> None:
    # TODO: Fix locale for production readiness.
    tts = ''

    user = db.get_user(m.from_user.id)
    if not user:
        user = db.create_user(m.from_user.id, m.from_user.first_name)
    tts += f'👤: {user.name} | 🆔: {user.id}\n'
    tts += f'🎟: {user.tickets}\n'
    tts += f'📈: {user.rating}\n'
    tts += f'🌍: {user.locale} (/locale)\n'

    await m.answer(**Text(tts).as_kwargs())


@r.message(Command("top_tickets"))
async def profile_handler(m: Message) -> None:
    tts = ''

    top = db.get_top_players_by_tickets()
    index = 0
    for user in top:
        if user.tickets <= 0:
            continue
        index += 1
        tts += f"{index}. {user.name} - {user.tickets}🎟\n"

    await m.answer(**Text(tts).as_kwargs())


@r.message(Command("give_ticket"))
async def profile_handler(m: Message) -> None:
    if (m.from_user.id not in config.admin_ids
            or not m.reply_to_message
            or not m.text.count(" ")):
        return

    user = db.get_user(m.reply_to_message.from_user.id)
    tickets = int(m.text.split(" ")[1])
    user.tickets += tickets

    db.commit()

    await m.answer(**Text("✅").as_kwargs())


@r.message(Command("locale"))
async def profile_handler(m: Message) -> None:
    tts = ''

    user = db.get_user(m.from_user.id)
    if not user:
        user = db.create_user(m.from_user.id, m.from_user.first_name)

    tts += ls("bot.common.locale.menu").format(ls(f"bot.locale.name")).localize(user.locale)

    kb = []
    for locale in translator.locales.keys():
        locale_text = ls(f"bot.locale.name").localize(locale)
        kb.append([InlineKeyboardButton(text=locale_text, callback_data=ChangeLocale(locale=locale).pack())])

    kb = InlineKeyboardMarkup(inline_keyboard=kb)

    await m.answer(tts, reply_markup=kb)
    return
