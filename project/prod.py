import os
import re
from dotenv import load_dotenv
import psycopg2
import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
)
from aiogram.fsm.state import StatesGroup, State
from aiogram import F
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('HOST'),
    'database': os.getenv('DATABASE'),
    'user': os.getenv('USER'),
    'password': os.getenv('PASSWORD')
}

logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()

class Form(StatesGroup):
    first_name: str = State()
    second_name: str = State()
    group: str = State()


def contains_bad_words(text):
    bad_words_patterns = [
        r'(?:\b|\W)бля\w*(?:\b|\W)', r'(?:\b|\W)говн\w*(?:\b|\W)', r'(?:\b|\W)гавн\w*(?:\b|\W)',
        r'(?:\b|\W)сука\w*(?:\b|\W)', r'(?:\b|\W)хуй\w*(?:\b|\W)', r'(?:\b|\W)хуе\w*(?:\b|\W)',
        r'(?:\b|\W)гонд\w*(?:\b|\W)', r'(?:\b|\W)пидо\w*(?:\b|\W)', r'(?:\b|\W)чмо\w*(?:\b|\W)',
        r'(?:\b|\W)ебла\w*(?:\b|\W)', r'(?:\b|\W)еба\w*(?:\b|\W)', r'(?:\b|\W)сучка\w*(?:\b|\W)',
        r'(?:\b|\W)заеб\w*(?:\b|\W)', r'(?:\b|\W)заёб\w*(?:\b|\W)', r'(?:\b|\W)мраз\w*(?:\b|\W)',
        r'(?:\b|\W)ебал\w*(?:\b|\W)', r'(?:\b|\W)пизд\w*(?:\b|\W)', r'(?:\b|\W)ебуч\w*(?:\b|\W)',
        r'(?:\b|\W)шлюх\w*(?:\b|\W)', r'(?:\b|\W)шлюш\w*(?:\b|\W)', r'(?:\b|\W)гей\w*(?:\b|\W)',
        r'(?:\b|\W)тупо\w*(?:\b|\W)', r'(?:\b|\W)залуп\w*(?:\b|\W)', r'(?:\b|\W)пенис\w*(?:\b|\W)',
        r'(?:\b|\W)член\w*(?:\b|\W)', r'(?:\b|\W)хули\w*(?:\b|\W)', r'(?:\b|\W)путана\w*(?:\b|\W)',
        r'(?:\b|\W)дрочила\w*(?:\b|\W)', r'(?:\b|\W)пердун\w*(?:\b|\W)', r'(?:\b|\W)малаф\w*(?:\b|\W)',
        r'(?:\b|\W)http\w*(?:\b|\W)'
    ]

    pattern = re.compile('|'.join(bad_words_patterns), flags=re.IGNORECASE | re.UNICODE)
    match = pattern.search(text)

    return bool(match)


@dp.message(F.new_chat_members)
async def somebody_added(message: types.Message):
    for user in message.new_chat_members:
        await message.answer(
            f"У нас в группе пополнение!\n"
            f"Добро пожаловать {user.full_name}"
        )


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"Привет, {message.from_user.full_name}.\n"
        f"Нажми на -> /help <- чтобы подробнее ознакомиться с моим функционалом"
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        f"Доступные команды:\n"
        "\n/start - начало работы с ботом\n"
        "/reg - создание профиля\n"
        # "/learn - материалы на паре\n"
        # "/code - решаем задачки"
    )


@dp.message(Command("reg"))
async def cmd_reg(message: types.Message, state: FSMContext) -> None:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT COUNT(*) FROM forms WHERE tg_nickname = %s
            """,
            (message.from_user.username,)
        )
        result = cursor.fetchone()[0]

        if result > 0:
            await message.answer(
                f"У вас уже есть профиль с ником {message.from_user.username}. Регистрация не требуется."
            )
            return

        await message.answer(
            "Напишите свои Фамилию.\n"
            "Например: Иванов",
        )
        await state.set_state(Form.first_name)

    except Exception as e:
        await message.answer(f"Произошла ошибка при проверке регистрации: {e}")

    finally:
        cursor.close()
        conn.close()


@dp.message(Form.first_name)
async def process_first_name(message: Message, state: FSMContext) -> None:
    await state.update_data(first_name=message.text)
    await message.answer(
        "Напишите своё имя.\n"
        "Например: Иван"
    )
    await state.set_state(Form.second_name)


@dp.message(Form.second_name)
async def process_second_name(message: Message, state: FSMContext) -> None:
    await state.update_data(second_name=message.text)
    await message.answer(
        "Напишите свою группу.\n"
        "Например: АБ-12\n"
    )
    await state.set_state(Form.group)


@dp.message(Form.group)
async def process_group(message: Message, state: FSMContext) -> None:
    await state.update_data(group=message.text)
    user_data = await state.get_data()

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO forms (first_name, second_name, group_name, tg_nickname)
            VALUES (%s, %s, %s, %s)
            """,
            (user_data['first_name'], user_data['second_name'], user_data['group'], message.from_user.username)
        )

        conn.commit()

        await message.answer(
            f"Данные успешно сохранены в базу данных!\n"
            f"Фамилия - {user_data['first_name']}\n"
            f"Имя - {user_data['second_name']}\n"
            f"Группа - {user_data['group']}\n"
            f"Ник в тг - {message.from_user.username}"
        )

    except Exception as e:
        conn.rollback()
        await message.answer(f"Произошла ошибка при сохранении данных: {e}")

    finally:
        cursor.close()
        conn.close()

    await state.clear()


@dp.message(F.text)
async def check_for_bad_words(message: types.Message):
    if contains_bad_words(str(message.text)):
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    else:
        pass


@dp.edited_message(F.text)
async def check_for_bad_words(message: types.Message):
    if contains_bad_words(str(message.text)):
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    else:
        pass


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())