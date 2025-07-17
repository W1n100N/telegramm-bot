import asyncio
import logging
from aiogram import Bot, Dispatcher
from handlers import router
from database import init_db

logging.basicConfig(level=logging.INFO)
bot = Bot(token='7597838385:AAFhQ6tnznNENjrqA7s4RC28u79KUzmqtJY')
dp = Dispatcher()

async def main():
    await init_db()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())