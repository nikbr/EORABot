import asyncio
from aiogram import Bot, Dispatcher, types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.filters import Command
import nest_asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import json
import os
asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
nest_asyncio.apply()


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


bot = Bot(token=str(TELEGRAM_BOT_TOKEN))
dp = Dispatcher()

async def call_mcp_tool(tool_name, args):
    async with sse_client("http://eorabot:8050/sse") as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            return await session.call_tool(tool_name, arguments=args)

@dp.message(Command("start"))
async def start_cmd(msg: types.Message):
    await msg.answer("Здравствуйте! 👋 Я ассистент компании EORA.\nЗадайте любой вопрос о нашей компании.")

@dp.message()
async def answer_any(msg: types.Message):
    await msg.answer("Пожалуйста подождите ответа...")

    response = await call_mcp_tool("ask_question", {"question": msg.text})

    answer = response.content[0].model_dump()

    try:
        answer_data = json.loads(answer['text'])
        sources = answer["sources"]
        
    except Exception as e:
        await msg.answer("Ответ не был правильным JSONом. Пожалуйста попробуйте ещё раз.")
        return

    await msg.answer(
        "Спасибо за ваш вопрос! 🧠\n"
        "Компания <b>EORA</b> занимается разработкой инновационных цифровых решений.\n"
        "Если нужно, могу рассказать подробнее про продукты, миссию или команду."
    )

def run_bot():
    dp.run_polling(bot)

if __name__ == "__main__":
    asyncio.run(run_bot())