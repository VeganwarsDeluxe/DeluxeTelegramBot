import asyncio
import logging
import sys

import VegansDeluxe.core
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Update

import config
import game.content
from db import db
from handlers.callback_handlers import r as callbacks_router
from handlers.matches import r as match_router
from handlers.other import r as other_router
from handlers.profile import r as profile_router
from startup import engine, version

print(f"Imported {game.content}.\n")

dp = Dispatcher()


async def main() -> None:
    bot = Bot(token=config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    dp.include_router(match_router)
    dp.include_router(callbacks_router)
    dp.include_router(profile_router)
    dp.include_router(other_router)

    @dp.update.outer_middleware()
    async def database_middleware(handler, event: Update, data):
        await db.process_event(event)
        return await handler(event, data)

    await bot.send_message(
        config.boot_chat,
        f"♻️Core: `{VegansDeluxe.core.__version__}`\n"
        f"🤖Bot: `{version}`\n\n"
        f"📄Changelog: [here](https://github.com/VeganwarsDeluxe/VeganwarsDeluxe/blob/master/CHANGELOG.md)",
        parse_mode="Markdown"
    )
    print(engine.stats())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, stream=sys.stdout, force=True)
    asyncio.run(main())
