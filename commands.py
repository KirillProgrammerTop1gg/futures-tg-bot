from aiogram.filters import Command
from aiogram.types.bot_command import BotCommand

START_COMMAND = Command("start")
HELP_COMMAND = Command("help")
ADD_TO_WHITELIST_COMMAND = Command("add_user_to_whitelist")
GET_WHITELIST_COMMAND = Command("get_whitelist")
DEL_IN_WHITELIST_COMMAND = Command("del_user_in_whitelist")

START_BOT_COMMAND = BotCommand(command="start", description="Почати розмову")
HELP_BOT_COMMAND = BotCommand(command="help", description="Довідка про функції бота")
ADD_TO_WHITELIST_BOT_COMMAND = BotCommand(
    command="get_whitelist", description="Отримати вайтліст"
)
GET_WHITELIST_BOT_COMMAND = BotCommand(
    command="add_user_to_whitelist", description="Додати юзера у вайтліст"
)
DEL_IN_WHITELIST_BOT_COMMAND = BotCommand(
    command="del_user_in_whitelist", description="Видалити юзера із вайтліста"
)
