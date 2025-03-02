import datetime
import psycopg2
import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from form import Form
from test_usage.config import bToken

# date_time = datetime.datetime.now().strftime("%d.%m.%Y")
# work_time = datetime.datetime.now().strftime("%H:%M:%S")

# Конфигурация базы данных
DB_CONFIG = {
    'host': 'localhost',
    'database': 'postgres',
    'user': 'postgres',
    'password': '4242564'
}

logging.basicConfig(level=logging.INFO)
bot = Bot(token=bToken)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"Приветствую тебя, {message.from_user.full_name}.\n"
        f"Нажми на -> /help <- чтобы подробнее ознакомиться с моим функционалом"
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        f"Доступные команды:\n"
        "\n/start - начало работы с ботом\n"
        "/reg - создание профиля\n"
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


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())