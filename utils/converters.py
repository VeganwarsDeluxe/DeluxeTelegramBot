from aiogram.types import InlineKeyboardMarkup as aioIKM
from aiogram.types import InlineKeyboardButton as aioIKB
from telebot.types import InlineKeyboardMarkup as telebotIKM
from telebot.types import InlineKeyboardButton as telebotIKB


def aio_to_telebot_inline_keyboard(aio_kb: aioIKM) -> telebotIKM:
    kb = telebotIKM()
    for aio_row in aio_kb.inline_keyboard:
        telebot_row = []
        for aio_button in aio_row:
            telebot_button = telebotIKB(text=aio_button.text, url=aio_button.url,
                                        callback_data=aio_button.callback_data)
            telebot_row.append(telebot_button)

        kb.add(*telebot_row)
    return kb
