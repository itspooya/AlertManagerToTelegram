#!/usr/bin/env python
# pylint: disable=C0116
# This program is dedicated to the public domain under the CC0 license.

import datetime
import logging
import os

import pytz
import telegram
from telegram import Update, ForceReply, Bot
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    CallbackQueryHandler,
)
from emoji import emojize
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("TELEGRAM_TOKEN")
timezone = os.getenv("TIMEZONE")
bot = Bot(token)
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr"Hi {user.mention_markdown_v2()}\!",
        reply_markup=ForceReply(selective=True),
    )


def help_command(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text("Help!")


def resolved(update: Update, _: CallbackContext) -> None:
    query = update.callback_query
    print(query)
    query.answer("Done")
    update.callback_query.message.edit_text(
        emojize(
            f":white_check_mark: Resolved\n\n{query.message.text}\n\nEndTime: {datetime.datetime.now(pytz.timezone(timezone))}\n\nChecked by: {query.from_user.first_name} "
            f"@{query.from_user.username}",
            use_aliases=True,
        )
    )


def check(update: Update, _: CallbackContext) -> None:
    query = update.callback_query

    # print(query)
    query.answer("Done")
    kb = [
        [telegram.InlineKeyboardButton(text="Resolved", callback_data="/resolved")],
        [telegram.InlineKeyboardButton(text="Delete", callback_data="/delete")],
        [telegram.InlineKeyboardButton(text="False", callback_data="/false")],
    ]
    kb_markup = telegram.InlineKeyboardMarkup(kb, one_time_keyboard=True)
    update.callback_query.message.edit_text(
        f"{query.message.text}\n\n Will be checked by: {query.from_user.first_name}"
        f" @{query.from_user.username}\n\nAcknowledged Time: {datetime.datetime.now(pytz.timezone(timezone))}",
        reply_markup=kb_markup,
    )


def delete(update: Update, _: CallbackContext) -> None:
    query = update.callback_query
    query.answer("Done")
    update.callback_query.message.delete()


def false_alert(update: Update, _: CallbackContext) -> None:
    query = update.callback_query
    query.answer("Done")
    update.callback_query.message.edit_text(
        emojize(
            f":negative_squared_cross_mark: False Alert\n\n{query.message.text}"
            f"\n\n EndTime: {datetime.datetime.now(pytz.timezone(timezone))}\n\nChecked by: {query.from_user.first_name} "
            f"@{query.from_user.username}",
            use_aliases=True,
        )
    )


def echo(update: Update, _: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(token, request_kwargs={"read_timeout": 6, "connect_timeout": 7})

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(
        CallbackQueryHandler(resolved, pattern="^" + str("/resolved") + "$")
    )
    dispatcher.add_handler(
        CallbackQueryHandler(check, pattern="^" + str("/check") + "$")
    )
    dispatcher.add_handler(
        CallbackQueryHandler(delete, pattern="^" + str("/delete") + "$")
    )
    dispatcher.add_handler(
        CallbackQueryHandler(false_alert, pattern="^" + str("/false") + "$")
    )
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
