from aiogram.utils.text_decorations import MarkdownDecoration
from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters.command import Command
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from logfire import instrument
import logfire
import logging
import asyncio
import os

from message_tools import MessageTools
from stt import NexaraSTT
import texts


load_dotenv()
TG_TOKEN = os.getenv("TG_TOKEN")
NEXARA_TOKEN = os.getenv("NEXARA_TOKEN")
LOGFIRE_TOKEN = os.getenv("LOGFIRE_TOKEN")
STT = NexaraSTT(NEXARA_TOKEN)

logfire.configure(token=LOGFIRE_TOKEN)
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TG_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2))
dp = Dispatcher()
md = MarkdownDecoration()


@dp.message(Command("start"))
@instrument("Processing start command")
async def cmd_start(message: types.Message):
    await MessageTools.send_response(message, texts.start_command)


@dp.message(F.voice)
@instrument("Processing voice message")
async def process_voice(message: types.Message, bot: Bot):
    """Handler for voice messages."""
    try:
        file_info = await bot.get_file(message.voice.file_id)

        logfire.info("Downloading voice file")
        downloaded_file = await bot.download_file(file_info.file_path)

        logfire.info("Starting audio transcription")
        data = await STT.audio_analyze(downloaded_file.read())
        
        await MessageTools.send_response(message, md.expandable_blockquote(data)[:-2])
    except Exception as e:
        logfire.error("Error processing voice message", error=str(e), _exc_info=True)
        await MessageTools.send_response(message, texts.stt_error.format(e))


@dp.message(F.video_note)
@instrument("Processing video note")
async def process_voice(message: types.Message, bot: Bot):
    """Handler for voice messages."""
    try:
        file_info = await bot.get_file(message.video_note.file_id)

        logfire.info("Downloading voice file")
        downloaded_file = await bot.download_file(file_info.file_path)

        logfire.info("Starting audio transcription")
        data = await STT.audio_analyze(downloaded_file.read())
        
        await MessageTools.send_response(message, md.expandable_blockquote(data)[:-2])
    except Exception as e:
        logfire.error("Error processing voice message", error=str(e), _exc_info=True)
        await MessageTools.send_response(message, texts.stt_error.format(e))


async def main():
    await dp.start_polling(bot)
    logfire.info("Bot has been started")

if __name__ == "__main__":
    asyncio.run(main())