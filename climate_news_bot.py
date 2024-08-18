import asyncio
from aiogram import executor
from dispatcher import dp
import handlers

if __name__ == "__main__":

    # 1. Start workers
    loop = asyncio.get_event_loop()

    # 2. Start bot
    executor.start_polling(dp, skip_updates=False)
