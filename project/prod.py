import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
)

from form import Form


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

# @dp.message(Command("theory"))
# async def cmd_document(message: types.Message):
#     await message.answer(f'База для {message.from_user.full_name}.')
#     doc_from_pc = FSInputFile("../static/glossary.doc")
#     await message.answer_document(
#         doc_from_pc,
#         caption="Данный файл должен служить началом для Вашей работы"
#     )
#     doc_from_pc = FSInputFile("../static/naming.doc")
#     await message.answer_document(
#         doc_from_pc,
#         caption="Данный файл должен стать базой Вашего 'стартаперского сленга'"
#     )


@dp.message(Command("reg"))
async def cmd_reg(message: types.Message, state: FSMContext) -> None:
    await message.answer(
        "Напишите свои Фамилию.\n"
        "Например:Иванов",
    )
    await state.set_state(Form.first_name)


@dp.message(Form.first_name)
async def process_first_name(message: Message, state: FSMContext) -> None:
    await state.update_data(first_name=message.text)
    await message.answer(
        "Напишите своё имя.\n"
        "Например:Иван"
    )
    await state.set_state(Form.second_name)


@dp.message(Form.second_name)
async def process_second_name(message: Message, state: FSMContext) -> None:
    await state.update_data(second_name=message.text)
    await message.answer(
        "Напишите свою группу.\n"
        "Например:АБ-12\n"
    )
    await state.set_state(Form.group)


@dp.message(Form.group)
async def process_group(message: Message, state: FSMContext) -> None:
    await state.update_data(group=message.text)
    user_data = await state.get_data()
    await message.answer(
        f"Вы ввели:\n"
        f"Фамилия - {user_data['first_name']}\n"
        f"Имя - {user_data['second_name']}\n"
        f"Группа - {user_data['group']}"
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
