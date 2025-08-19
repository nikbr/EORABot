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
from lib.config import TELEGRAM_BOT_TOKEN, SERVER_HOST
import re
from typing import Callable

bot = Bot(token=str(TELEGRAM_BOT_TOKEN))
dp = Dispatcher()



async def call_mcp_tool(tool_name, args):
    async with sse_client(f"{SERVER_HOST}:8050/sse") as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            return await session.call_tool(tool_name, arguments=args)

async def do_with_retries(operation: Callable, *args, retries:int = 1):
    for _ in range(retries+1):
        try:
            return await operation(*args)
        except Exception:
            continue
    raise Exception("All retries failed.")


@dp.message(Command("start"))
async def start_cmd(msg: types.Message):
    await msg.answer("Здравствуйте! 👋 Я ассистент компании EORA.\nЗадайте любой вопрос о нашей компании.")

@dp.message()
async def answer_any(msg: types.Message):
    await msg.answer("Пожалуйста подождите ответа...")
    await do_with_retries(answer_any_helper, msg, retries=1)



async def answer_any_helper(msg: types.Message):
    response = await call_mcp_tool("ask_question", {"question": msg.text})

    answer = response.content[0].model_dump()

    try:
        print("answer:", answer, flush=True)
        answer_data = json.loads(answer['text'])
        sources = answer_data["sources"]

        def replace_reference(match):
            num = match.group(1)
            if num in sources: url = sources[num]
            else:
                raise
            return f'<a href="{url}">[{num}]</a>'

        result = re.sub(r'\[(\d+)\]', replace_reference, answer_data["text"])
        await msg.answer(result, parse_mode="HTML")

    except Exception as e:
        await msg.answer("Пожалуйста попробуйте ещё раз.")
        return

def run_bot():
    dp.run_polling(bot)

if __name__ == "__main__":
    asyncio.run(run_bot())