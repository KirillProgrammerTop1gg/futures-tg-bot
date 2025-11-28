from aiogram.filters import Command
from aiogram.types.bot_command import BotCommand

START_COMMAND = Command("start")
HELP_COMMAND = Command("help")
ADD_TO_WHITELIST_COMMAND = Command("add_user_to_whitelist")
GET_WHITELIST_COMMAND = Command("get_whitelist")
DEL_IN_WHITELIST_COMMAND = Command("del_user_in_whitelist")
SET_TRADE_INFO_COMMAND = Command("set_trade_info")
GET_CONTRACTS_INFO_COMMAND = Command("get_contracts_info")
GET_PRICES_COMMAND = Command("get_prices")
OPEN_ORDER_COMMAND = Command("open_order")


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
SET_TRADE_INFO_BOT_COMMAND = BotCommand(
    command="set_trade_info", description="Редагувати інформацію для трейдингу"
)
GET_CONTRACTS_INFO_BOT_COMMAND = BotCommand(
    command="get_contracts_info",
    description="Отримати інформацію про контракти токена на біржах",
)
GET_PRICES_BOT_COMMAND = BotCommand(
    command="get_prices",
    description="Отримати ціни токена на різних біржах та в різних напрямках",
)
OPEN_ORDER_BOT_COMMAND = BotCommand(command="open_order", description="Відкрити ордера")
