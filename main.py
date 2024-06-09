import asyncio
import logging
import sys

import VegansDeluxe.core
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import config

from handlers.matches import r as match_router
from handlers.callbacks import r as callbacks_router
from handlers.other import r as other_router
from startup import engine, version

dp = Dispatcher()


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp.include_router(match_router)
    dp.include_router(callbacks_router)
    dp.include_router(other_router)

    # And the run events dispatching
    await bot.send_message(config.boot_chat,
                           f"♻️Core: `{VegansDeluxe.core.__version__}`\n"
                           f"🤖Bot: `{version}`\n\n"
                           f"📄Latest changelog: ```"
                           f"\n - 100% is now localized. Access with Deluxe Premium only"
                           f"\n - reworking bot internals (not the core)"
                           f"```",
                           parse_mode="Markdown")
    print(engine.stats())

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
