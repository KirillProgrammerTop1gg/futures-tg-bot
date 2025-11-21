from config import BOT_TOKEN, BYBIT_KEYS, BINANCE_KEYS, OKX_KEYS
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.types import Message, CallbackQuery
from aiogram import F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from commands import (
    START_COMMAND,
    HELP_COMMAND,
    ADD_TO_WHITELIST_COMMAND,
    GET_WHITELIST_COMMAND,
    DEL_IN_WHITELIST_COMMAND,
    START_BOT_COMMAND,
    HELP_BOT_COMMAND,
    GET_WHITELIST_BOT_COMMAND,
    ADD_TO_WHITELIST_BOT_COMMAND,
    DEL_IN_WHITELIST_BOT_COMMAND,
)
from data.data import get_whitelist, add_to_whitelist, del_in_whitelist
from keyboards import (
    RoleCallback,
    role_keyboard_markup,
    UsersCallback,
    users_keyboard_markup,
)
from typing import Optional, Union, Dict, List
from models import User
from exchanges_API import exchanges_API

dp = Dispatcher()


class WhiteListForm(StatesGroup):
    name = State()
    id = State()
    role = State()


def get_ids_from_whitelist(whitelist: List[Dict[str, int]]) -> List[int]:
    return list(map(lambda x: x["id"], whitelist))


async def allow_user(message: Message) -> bool:
    expr = message.from_user.id in get_ids_from_whitelist(get_whitelist())
    if not expr:
        await message.answer(
            "Ви не знаходитесь у вайтлісті, запитайте адміністратора, щоб він вас додав або ідіть геть!"
        )
    return expr


def allow_user_admin(message: Message) -> bool:
    return message.from_user.id in get_ids_from_whitelist(
        list(filter(lambda x: x["role"] == "admin", get_whitelist()))
    )


@dp.message(START_COMMAND, allow_user)
async def start(message: Message) -> None:
    await message.answer(
        f"Доброго дня, {message.from_user.full_name}!\nЦей бот створений для одночасного відкриття фьючерсних угод на біржах в різні сторони"
    )


@dp.message(GET_WHITELIST_COMMAND, allow_user)
async def show_whitelist(message: Message) -> None:
    await message.answer(
        f"Вайтліст:\n{''.join([f"Ім'я: {allowed_user['name']}, Роль: {allowed_user['role']}, Id: {allowed_user['id']}\n" for allowed_user in get_whitelist()])}"
    )


@dp.message(ADD_TO_WHITELIST_COMMAND, allow_user_admin)
async def send_whitelist(message: Message, state: FSMContext) -> None:
    await message.answer("Відправте контакт людини, якої ви хочете додати у вайтліст")
    await state.set_state(WhiteListForm.name)


@dp.message(allow_user, WhiteListForm.name, F.contact)
async def handle_user_or_contact(message: Message, state: FSMContext) -> None:
    await state.update_data(
        name=f"{message.contact.first_name} {message.contact.last_name or ''}",
        id=message.contact.user_id,
    )
    await state.set_state(WhiteListForm.role)
    data = role_keyboard_markup()
    await message.answer(f"Оберіть роль користувача", reply_markup=data)


@dp.callback_query(RoleCallback.filter())
async def callb_role(
    callback: CallbackQuery, callback_data: RoleCallback, state: FSMContext
) -> None:
    await state.update_data(role=callback_data.role)

    new_user_data = await state.get_data()
    await state.clear()

    try:
        new_user = User(**new_user_data)
        add_to_whitelist(new_user.model_dump())
        await callback.message.answer("Нового користувача успішно додано у вайт ліст!")
    except ValueError:
        await callback.message.answer("Помилка в додаванні! Спробуйте ще раз")
        await state.set_state(WhiteListForm.name)
    await callback.message.delete()


@dp.message(DEL_IN_WHITELIST_COMMAND, allow_user_admin)
async def send_whitelist(message: Message, state: FSMContext) -> None:
    markup_data = users_keyboard_markup(get_whitelist())
    await message.answer("Оберіть юзера для видалення", reply_markup=markup_data)


@dp.callback_query(UsersCallback.filter())
async def callb_user(callback: CallbackQuery, callback_data: UsersCallback) -> None:
    userId = callback_data.id
    if callback.from_user.id == userId:
        await callback.message.answer(f"Ви не можете видалити самого себе!")
    else:
        del_in_whitelist(userId)
        await callback.message.answer(f"Юзер успішно видален з вайтліста")
    await callback.message.delete()


async def main() -> None:
    bot = Bot(token=BOT_TOKEN)
    await bot.set_my_commands(
        [
            START_BOT_COMMAND,
            HELP_BOT_COMMAND,
            GET_WHITELIST_BOT_COMMAND,
            ADD_TO_WHITELIST_BOT_COMMAND,
            DEL_IN_WHITELIST_BOT_COMMAND,
        ]
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
