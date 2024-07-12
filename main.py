from VegansDeluxe.core import EventContext, Event, At

import game.content

import asyncio
import logging
import sys

import VegansDeluxe.core
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import config

from handlers.matches import r as match_router
from handlers.callback_handlers import r as callbacks_router
from handlers.other import r as other_router
from startup import engine, version

print(f"Imported {game.content}.\n")

dp = Dispatcher()


async def main() -> None:
    bot = Bot(token=config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp.include_router(match_router)
    dp.include_router(callbacks_router)
    dp.include_router(other_router)

    await bot.send_message(config.boot_chat,
                           f"♻️Core: `{VegansDeluxe.core.__version__}`\n"
                           f"🤖Bot: `{version}`\n\n"
                           f"📄Latest changelog: ```"
                           f"\n - fixed necromancer localization (but not the skill itself)"
                           f"\n - nothing is crashing again! try out new matches!"
                           f"\n/vd_bots is stable"
                           f"\ninitial work at deathmatch"
                           f"```",
                           parse_mode="Markdown")
    print(engine.stats())

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, force=True)
    asyncio.run(main())
