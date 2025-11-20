from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from typing import List, Dict


class RoleCallback(CallbackData, prefix="role", sep=";"):
    role: str


def role_keyboard_markup():
    builder = InlineKeyboardBuilder()
    builder.adjust(1, repeat=True)

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
