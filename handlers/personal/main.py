from aiogram import types
from dispatcher import dp
from filters import IsPersonalMsgFilter

# Main handler
@dp.message_handler(IsPersonalMsgFilter(), content_types=types.ContentType.ANY)
async def main(message: types.Message):
    message.reply("Presonal messages are not allowed.")
