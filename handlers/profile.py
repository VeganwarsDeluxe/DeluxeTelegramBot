from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.formatting import Text

from db import db

r = Router()


@r.message(Command("profile"))
async def profile_handler(m: Message) -> None:
    tts = ''

    user = db.get_user(m.from_user.id)
    if not user:
        user = db.create_user(m.from_user.id, m.from_user.first_name)
    tts += f'👤: {user.name} | 🆔: {user.id}\n'
    tts += f'🎟: {user.tickets}\n'
    tts += f'📈: {user.rating}\n'
    tts += f'🌍: {user.locale} (/locale)\n'

    await m.answer(**Text(tts).as_kwargs())


@r.message(Command("locale"))
async def profile_handler(m: Message) -> None:
    # TODO: Rewrite this. Locale choice should be with buttons.
    #  Also checking for locale in the list is wrong. Overall design was written in a hurry.
    tts = ''

    user = db.get_user(m.from_user.id)
    if not user:
        user = db.create_user(m.from_user.id, m.from_user.first_name)

    if m.text.count(' ') != 1:
        tts += f'🌍: {user.locale}\n\n'
        tts += f'🇺🇦: /locale uk\n'
        tts += f"🇷🇺: /locale ru\n"
        tts += f'🇬🇧: /locale en\n'
        await m.answer(**Text(tts).as_kwargs())
        return

    locale = m.text.split(' ')[1]
    if locale not in ['uk', 'en', 'ru']:
        await m.answer("❌")
        return

    tts += '✅'
    db.change_locale(m.from_user.id, locale)
    await m.answer(**Text(tts).as_kwargs())
