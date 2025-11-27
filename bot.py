from config import BOT_TOKEN, BYBIT_KEYS, BINANCE_KEYS, OKX_KEYS
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.types import Message, CallbackQuery
from aiogram import F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from commands import (
    START_COMMAND,
    HELP_COMMAND,
    ADD_TO_WHITELIST_COMMAND,
    GET_WHITELIST_COMMAND,
    DEL_IN_WHITELIST_COMMAND,
    SET_TRADE_INFO_COMMAND,
    GET_CONTRACTS_INFO_COMMAND,
    GET_PRICES_COMMAND,
    START_BOT_COMMAND,
    HELP_BOT_COMMAND,
    GET_WHITELIST_BOT_COMMAND,
    ADD_TO_WHITELIST_BOT_COMMAND,
    DEL_IN_WHITELIST_BOT_COMMAND,
    SET_TRADE_INFO_BOT_COMMAND,
    GET_CONTRACTS_INFO_BOT_COMMAND,
    GET_PRICES_BOT_COMMAND,
)
from data.data import get_whitelist, add_to_whitelist, del_in_whitelist
from keyboards import (
    RoleCallback,
    role_keyboard_markup,
    UsersCallback,
    users_keyboard_markup,
    ExchangeCallback,
    exchange_keyboard_markup,
    PriceStopCallback,
    price_stop_keyboard_markup,
)
from typing import Optional, Union, Dict, List
from models import User
from exchanges_API import exchanges_API

dp = Dispatcher()
exch_apis = exchanges_API(BINANCE_KEYS, BYBIT_KEYS, OKX_KEYS)

trades_info_storage = MemoryStorage()
update_tasks = {}


class WhiteListForm(StatesGroup):
    name = State()
    id = State()
    role = State()


class TradeInfo(StatesGroup):
    exchange1 = State()
    exchange2 = State()
    symbol = State()


def get_ids_from_whitelist(whitelist: List[Dict[str, int]]) -> List[int]:
    return list(map(lambda x: x["id"], whitelist))


async def allow_user(message: Message) -> bool:
    expr = message.from_user.id in get_ids_from_whitelist(get_whitelist())
    if not expr:
        await message.answer(
            "Ви не знаходитесь у вайтлісті, запитайте адміністратора, щоб він вас додав або ідіть геть!"
        )
    return expr


async def update_trade_info_data(id) -> None:
    exch_apis.clean_info()
    trade_info = await trades_info_storage.get_data(f"trade_info_{id}")
    if trade_info:
        exch_apis.exchanges = trade_info["exchanges"]
        exch_apis.symbol = trade_info["symbol"]


async def is_trade_info(message: Message) -> bool:
    await update_trade_info_data(message.from_user.id)
    is_info = exch_apis.is_enough_info()
    if not is_info:
        await message.answer(
            "Ви ще не додали інформацію для трейдинга\n"
            "Спробуйте використати команду: /set_trade_info"
        )
    return is_info


def allow_user_admin(message: Message) -> bool:
    return message.from_user.id in get_ids_from_whitelist(
        list(filter(lambda x: x["role"] == "admin", get_whitelist()))
    )


async def update_price_message(sent_message, markup):
    try:
        while True:
            await asyncio.sleep(1.5)
            text = exch_apis.get_prices()
            await sent_message.edit_text(text, reply_markup=markup)
    except asyncio.CancelledError:
        text = exch_apis.get_prices()
        await sent_message.edit_text(text)


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
async def send_whitelist(message: Message) -> None:
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


@dp.message(SET_TRADE_INFO_COMMAND, allow_user)
async def set_trade_info(message: Message, state: FSMContext) -> None:
    await message.answer(
        f"Оберіть першу біржу для оновлення інформації по трейдингу",
        reply_markup=exchange_keyboard_markup(),
    )
    await state.set_state(TradeInfo.exchange1)


@dp.callback_query(ExchangeCallback.filter(), TradeInfo.exchange1)
async def callb_first_exchange(
    callback: CallbackQuery, callback_data: ExchangeCallback, state: FSMContext
) -> None:
    await state.update_data(exchange1=callback_data.exchange)
    await callback.message.edit_text(
        f"Оберіть другу біржу для оновлення інформації по трейдингу",
        reply_markup=exchange_keyboard_markup(),
    )
    await state.set_state(TradeInfo.exchange2)


@dp.callback_query(ExchangeCallback.filter(), TradeInfo.exchange2)
async def callb_second_exchange(
    callback: CallbackQuery, callback_data: ExchangeCallback, state: FSMContext
) -> None:
    trade_info_data = await state.get_data()
    exchange1 = trade_info_data["exchange1"]
    exchange2 = callback_data.exchange
    if exchange2 == exchange1:
        await callback.message.answer(
            f"Ви не можете обрати теж саму біржу!\n"
            f"Оберіть ще раз другу біржу для трейдингу",
            reply_markup=exchange_keyboard_markup(),
        )
    else:
        await callback.message.answer(f"Дякую! Ведіть символ для торгівлі")
        await state.update_data(exchange2=callback_data.exchange)
        await state.set_state(TradeInfo.symbol)
    await callback.message.delete()


@dp.message(allow_user, TradeInfo.symbol, F.text)
async def handle_trade_info_symbol(message: Message, state: FSMContext) -> None:
    trade_info_data = await state.get_data()
    user_id = message.from_user.id
    await state.clear()
    await message.answer(f"Вся інформація зберіглась, дякую!")
    await trades_info_storage.update_data(
        f"trade_info_{user_id}",
        {
            "exchanges": [trade_info_data["exchange1"], trade_info_data["exchange2"]],
            "symbol": message.text.upper(),
        },
    )


@dp.message(GET_CONTRACTS_INFO_COMMAND, allow_user, is_trade_info)
async def get_contracts_info(message: Message) -> None:
    text = exch_apis.get_contracts_info()
    await message.answer(text)


@dp.message(GET_PRICES_COMMAND, allow_user, is_trade_info)
async def get_prices(message: Message) -> None:
    text = exch_apis.get_prices()
    markup = price_stop_keyboard_markup()
    sent_msg = await message.answer(text, reply_markup=markup)
    task = asyncio.create_task(update_price_message(sent_msg, markup))
    update_tasks[message.from_user.id] = task


@dp.callback_query(PriceStopCallback.filter())
async def stop_prices(callback: CallbackQuery):
    id = callback.from_user.id
    task = update_tasks.get(id)
    if task:
        task.cancel()
        del update_tasks[id]
    await callback.answer()


async def main() -> None:
    bot = Bot(token=BOT_TOKEN)
    await bot.set_my_commands(
        [
            START_BOT_COMMAND,
            HELP_BOT_COMMAND,
            GET_WHITELIST_BOT_COMMAND,
            ADD_TO_WHITELIST_BOT_COMMAND,
            DEL_IN_WHITELIST_BOT_COMMAND,
            SET_TRADE_INFO_BOT_COMMAND,
            GET_CONTRACTS_INFO_BOT_COMMAND,
            GET_PRICES_BOT_COMMAND,
        ]
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
