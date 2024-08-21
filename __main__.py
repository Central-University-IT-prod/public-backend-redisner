import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

import handlers.locations.callback as locations_callback
import handlers.locations.messages as locations_messages
import handlers.main_menu.callback as main_menu_callback
import handlers.main_menu.messages as main_menu_messages
import handlers.travel.callback as travel_callback
import handlers.travel.inline as travel_inline
import handlers.travel.messages as travel_messages
import handlers.travel_notes.callback as notes_callback
import handlers.travel_notes.messages as notes_messages
import handlers.user_info.callback as user_info_callback
import handlers.user_info.messages as user_info_messages
from config import config


async def main():
    logging.basicConfig(level=logging.INFO)

    dp = Dispatcher(storage=RedisStorage(redis=Redis(host=config.REDIS_HOST.get_secret_value(),
                                                     port=config.REDIS_PORT)))

    bot = Bot(token=config.BOT_TOKEN.get_secret_value(),
              default=DefaultBotProperties(
                  parse_mode=ParseMode.HTML
              ))

    dp.include_router(main_menu_messages.router)
    dp.include_router(main_menu_callback.router)

    dp.include_router(user_info_messages.router)
    dp.include_router(user_info_callback.router)

    dp.include_router(travel_messages.router)
    dp.include_router(travel_callback.router)
    dp.include_router(travel_inline.router)

    dp.include_router(locations_messages.router)
    dp.include_router(locations_callback.router)

    dp.include_router(notes_messages.router)
    dp.include_router(notes_callback.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
