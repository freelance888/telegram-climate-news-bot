from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import BOT_TOKEN
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# prerequisites
if not BOT_TOKEN:
    exit("No token provided")

# init
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())
