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


START_BOT_COMMAND = BotCommand(
    command="start", description="Привітання та короткий вступ до функцій бота"
)
HELP_BOT_COMMAND = BotCommand(
    command="help", description="Детальна довідка про команди та роботу бота"
)
ADD_TO_WHITELIST_BOT_COMMAND = BotCommand(
    command="add_user_to_whitelist",
    description="Додати користувача до вайтліста, щоб він міг відкривати ордера",
)
GET_WHITELIST_BOT_COMMAND = BotCommand(
    command="get_whitelist",
    description="Переглянути список користувачів, які знаходяться у вайтлісті",
)
DEL_IN_WHITELIST_BOT_COMMAND = BotCommand(
    command="del_user_in_whitelist", description="Видалити користувача з вайтліста"
)
SET_TRADE_INFO_BOT_COMMAND = BotCommand(
    command="set_trade_info",
    description="Встановити або оновити інформацію для трейдингу: біржі та символи",
)
GET_CONTRACTS_INFO_BOT_COMMAND = BotCommand(
    command="get_contracts_info",
    description="Отримати деталі контрактів токена на біржах: мінімум, максимум, крок",
)
GET_PRICES_BOT_COMMAND = BotCommand(
    command="get_prices",
    description="Отримати актуальні ціни токена на різних біржах у різних напрямках",
)
OPEN_ORDER_BOT_COMMAND = BotCommand(
    command="open_order", description="Відкрити ордери на ф'ючерсних біржах одночасно"
)
OMMAND = BotCommand(command="open_order", description="Відкрити ордера")
