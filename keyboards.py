from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from typing import List, Dict


class RoleCallback(CallbackData, prefix="role", sep=";"):
    role: str


def role_keyboard_markup():
    builder = InlineKeyboardBuilder()
    builder.adjust(2, repeat=True)

    builder.button(text="юзер", callback_data=RoleCallback(role="user"))
    builder.button(text="адмін", callback_data=RoleCallback(role="admin"))

    return builder.as_markup()


class UsersCallback(CallbackData, prefix="users", sep=";"):
    id: int


def users_keyboard_markup(users):
    builder = InlineKeyboardBuilder()
    builder.adjust(1, repeat=True)

    for user in users:
        builder.button(
            text=f"{user['name']} - {user['id']}",
            callback_data=UsersCallback(id=user["id"]),
        )

    return builder.as_markup()


class ExchangeCallback(CallbackData, prefix="exchange", sep=";"):
    exchange: str


def exchange_keyboard_markup():
    builder = InlineKeyboardBuilder()
    builder.adjust(3, repeat=True)

    exchanges = ["Binance", "Bybit", "OKX"]

    for exchange in exchanges:
        builder.button(
            text=exchange, callback_data=ExchangeCallback(exchange=exchange.lower())
        )

    return builder.as_markup()


class PriceStopCallback(CallbackData, prefix="price_stop", sep=";"):
    is_stop: bool


def price_stop_keyboard_markup():
    builder = InlineKeyboardBuilder()
    builder.adjust(1, repeat=True)

    builder.button(
        text="Перестати оновлювати ціну", callback_data=PriceStopCallback(is_stop=True)
    )

    return builder.as_markup()
