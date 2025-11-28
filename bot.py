from config import BOT_TOKEN, BYBIT_KEYS, BINANCE_KEYS, OKX_KEYS
import asyncio, logging, sys
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
    OPEN_ORDER_COMMAND,
    GET_PRICES_COMMAND,
    START_BOT_COMMAND,
    HELP_BOT_COMMAND,
    GET_WHITELIST_BOT_COMMAND,
    ADD_TO_WHITELIST_BOT_COMMAND,
    DEL_IN_WHITELIST_BOT_COMMAND,
    SET_TRADE_INFO_BOT_COMMAND,
    GET_CONTRACTS_INFO_BOT_COMMAND,
    GET_PRICES_BOT_COMMAND,
    OPEN_ORDER_BOT_COMMAND,
)
from data.data import get_whitelist, add_to_whitelist, del_in_whitelist
from keyboards import (
    RoleCallback,
    role_keyboard_markup,
    UsersCallback,
    users_keyboard_markup,
    ExchangeCallback,
    exchange_keyboard_markup,
    ActionCallback,
    action_keyboard_markup,
)
from typing import Optional, Union, Dict, List
from models import User
from exchanges_API import exchanges_API

dp = Dispatcher()
exch_apis = exchanges_API(BINANCE_KEYS, BYBIT_KEYS, OKX_KEYS)

trades_info_storage = MemoryStorage()
update_tasks = {}
base_exchanges_list = ["binance", "bybit", "okx"]
exchanges_table = {"binance": "Binance", "bybit": "Bybit", "okx": "OKX"}


class WhiteListForm(StatesGroup):
    name = State()
    id = State()
    role = State()


class TradeInfo(StatesGroup):
    exchange1 = State()
    exchange2 = State()
    symbol = State()


class NewOrder(StatesGroup):
    lond_side_exchange = State()
    qty = State()
    cycles = State()


def get_ids_from_whitelist(whitelist: List[Dict[str, int]]) -> List[int]:
    return list(map(lambda x: x["id"], whitelist))


def format_exchanges_names(exchanges: List[str]) -> List[str]:
    return list(map(lambda x: exchanges_table.get(x, x), exchanges))


async def allow_user(message: Message) -> bool:
    expr = message.from_user.id in get_ids_from_whitelist(get_whitelist())
    if not expr:
        await message.answer(
            "Ви не в білому списку. Зверніться до адміністратора, щоб вас додали."
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
            "Ви ще не додали інформацію для трейдингу\n"
            "Спробуйте використати команду: /set_trade_info"
        )
    return is_info


def allow_user_admin(message: Message) -> bool:
    return message.from_user.id in get_ids_from_whitelist(
        list(filter(lambda x: x["role"] == "admin", get_whitelist()))
    )


async def update_price_message(message: Message, markup, base_text: str = "") -> None:
    text = exch_apis.get_prices()
    sent_message = await message.answer(f"{base_text}{text}", reply_markup=markup)
    while True:
        text = exch_apis.get_prices()
        try:
            await sent_message.edit_text(f"{base_text}{text}", reply_markup=markup)
            await asyncio.sleep(1.5)
        except asyncio.CancelledError:
            await sent_message.edit_text(f"{base_text}{text}")
            break


@dp.message(START_COMMAND, allow_user)
async def start(message: Message) -> None:
    await message.answer(
        f"Доброго дня, {message.from_user.full_name}!\n\n"
        "Цей бот дозволяє одночасно відкривати ф'ючерсні ордера на різних біржах у різні напрямки.\n\n"
        "Щоб дізнатися більше про команди та як користуватися ботом, використайте /help."
    )


@dp.message(HELP_COMMAND, allow_user)
async def help(message: Message) -> None:
    await message.answer(
        "Бот дозволяє керувати трейдингом ф'ючерсів на різних біржах одночасно.\n\n"
        "Модулі роботи:\n"
        "1️⃣ Вайтлист — додавання та видалення користувачів, які можуть відкривати ордера. "
        "Якщо користувача немає у вайтлісті, бот не відповідатиме йому.\n"
        "2️⃣ Торгівля — оновлення інформації про трейд (біржі, символи), отримання цін та інформації про контракти (мінімум, максимум, крок), відкриття ордерів.\n\n"
        "Доступні команди:\n"
        "/start — Почати розмову\n"
        "/help — Довідка про функції бота\n"
        "/add_user_to_whitelist — Додати юзера у вайтліст\n"
        "/get_whitelist — Отримати вайтліст\n"
        "/del_user_in_whitelist — Видалити юзера із вайтліста\n"
        "/set_trade_info — Редагувати інформацію для трейдингу\n"
        "/get_contracts_info — Отримати інформацію про контракти токена на біржах\n"
        "/get_prices — Отримати ціни токена на різних біржах та в різних напрямках\n"
        "/open_order — Відкрити ордера"
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
        await callback.message.answer("Ви не можете видалити самого себе!")
    else:
        del_in_whitelist(userId)
        await callback.message.answer("Юзер успішно видалено з вайтліста")
    await callback.message.delete()


@dp.message(SET_TRADE_INFO_COMMAND, allow_user)
async def set_trade_info(message: Message, state: FSMContext) -> None:
    await message.answer(
        f"Оберіть першу біржу для оновлення інформації по трейдингу",
        reply_markup=exchange_keyboard_markup(
            format_exchanges_names(base_exchanges_list)
        ),
    )
    await state.set_state(TradeInfo.exchange1)


@dp.callback_query(ExchangeCallback.filter(), TradeInfo.exchange1)
async def callb_first_exchange(
    callback: CallbackQuery, callback_data: ExchangeCallback, state: FSMContext
) -> None:
    await state.update_data(exchange1=callback_data.exchange)
    await callback.message.edit_text(
        f"Оберіть другу біржу для оновлення інформації по трейдингу",
        reply_markup=exchange_keyboard_markup(
            format_exchanges_names(base_exchanges_list)
        ),
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
            f"Оберіть ще раз другу біржу для трейдингу\n",
            reply_markup=exchange_keyboard_markup(
                format_exchanges_names(base_exchanges_list)
            ),
        )
    else:
        await callback.message.answer(f"Дякую! Введіть символ для торгівлі")
        await state.update_data(exchange2=callback_data.exchange)
        await state.set_state(TradeInfo.symbol)
    await callback.message.delete()


@dp.message(TradeInfo.symbol, F.text)
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
    markup = action_keyboard_markup(
        [{"text": "Перестати оновлювати ціну", "data": "stop_price"}]
    )
    task = asyncio.create_task(update_price_message(message, markup))
    update_tasks[message.from_user.id] = task


@dp.message(OPEN_ORDER_COMMAND, allow_user, is_trade_info)
async def open_order(message: Message, state: FSMContext) -> None:
    await state.set_state(NewOrder.lond_side_exchange)
    await message.answer(
        f"Оберіть біржу для сторони LONG: ",
        reply_markup=exchange_keyboard_markup(
            format_exchanges_names(exch_apis.exchanges)
        ),
    )


@dp.callback_query(ExchangeCallback.filter(), NewOrder.lond_side_exchange)
async def callb_long_side_exchange(
    callback: CallbackQuery, callback_data: ExchangeCallback, state: FSMContext
) -> None:
    callb_exch = callback_data.exchange
    await callback.message.edit_text(
        f"Обрані сторони ордерів на біржах:\n\n"
        f"LONG - {exchanges_table[callb_exch]}\n"
        f"SHORT - {exchanges_table[exch_apis.get_another_exchange(callb_exch)]}"
    )
    await callback.message.answer("Введіть на к-сть токенів для ордерів (qty>0)")
    await state.update_data(lond_side_exchange=callb_exch)
    await state.set_state(NewOrder.qty)


@dp.message(NewOrder.qty, F.text)
async def set_order_qty(message: Message, state: FSMContext) -> None:
    qty = message.text
    try:
        qty = float(qty)
        if qty <= 0:
            raise ValueError
    except ValueError:
        return await message.answer("Ви ввели не правильну к-сть!\n" "Спробуйте ще!")
    await message.answer("Введіть скільки разів відкривати ордера")
    await state.update_data(qty=qty)
    await state.set_state(NewOrder.cycles)


@dp.message(NewOrder.cycles, F.text)
async def set_order_cycles(message: Message, state: FSMContext) -> None:
    cycles = message.text
    try:
        cycles = int(cycles)
        if cycles <= 0:
            raise ValueError
    except ValueError:
        return await message.answer(
            "Ви ввели не правильну к-сть повторень (натуральне число)!\n"
            "Спробуйте ще!"
        )

    await state.update_data(cycles=cycles)

    await update_trade_info_data(message.from_user.id)
    order_data = await state.get_data()

    long_side_exchange = order_data["lond_side_exchange"]
    qty = order_data["qty"]
    cycles = order_data["cycles"]
    symbol = exch_apis.symbol

    markup = action_keyboard_markup(
        [
            {"text": "Перестати оновлювати ціну", "data": "stop_price"},
            {"text": "Розмістити ордер!", "data": "place_order"},
        ]
    )

    task = asyncio.create_task(
        update_price_message(
            message,
            markup,
            f"Сформований ордер:\n\n"
            f"  LONG(BUY) - {long_side_exchange}\n"
            f"  SHORT(SELL) - {exch_apis.get_another_exchange(long_side_exchange)}\n"
            f"  Кількість(QTY) - {qty} {symbol} x {cycles} = {qty*cycles} {symbol}\n\n",
        )
    )
    update_tasks[message.from_user.id] = task


@dp.callback_query(ActionCallback.filter())
async def stop_prices(
    callback: CallbackQuery, callback_data: ActionCallback, state: FSMContext
) -> None:
    await callback.answer()
    action = callback_data.action

    id = callback.from_user.id
    task = update_tasks.get(id)
    if task:
        task.cancel()
        del update_tasks[id]

    if action == "place_order":
        order_data = await state.get_data()
        long_side_exchange = order_data["lond_side_exchange"]
        qty = order_data["qty"]
        cycles = order_data["cycles"]
        symbol = exch_apis.symbol

        await callback.message.answer("Починаю розміщати ордера!")
        orders_ids = await exch_apis.place_orders(qty, cycles, long_side_exchange)
        await callback.message.answer(
            f"Розміщено ордера {cycles} раз по {qty} {symbol} на:\n"
            f"  -{long_side_exchange} (LONG)\n"
            f"  -{exch_apis.get_another_exchange(long_side_exchange)} (SHORT)\n\n"
            f"Id створених ордерів:\n"
            f'{''.join(f'   -{order_id}\n' for order_id in orders_ids)}'
        )


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
            OPEN_ORDER_BOT_COMMAND,
        ]
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
