#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

"""

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import urllib.request
import requests
import json
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# from PSQLpersist import PsqlPersistence

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    output = ""
    for user in context.chat_data.values():
        output = output + "{} : {} ".format(user.get("name"), user.get("score"))
    if not output:
        output = "None"
    update.message.reply_text(output)


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def test_command(update: Update, context: CallbackContext) -> None:
    print(context.chat_data)
    pass
    # user_id = update.effective_user.id
    # user_name = update.effective_user.first_name
    # update_score(user_id, user_name, update, context)
    # del user_id
    # del user_name


def set_command(update, context):
    answer = ' '.join(context.args)
    name = update.effective_user.first_name
    context.chat_data.update({"users": {}})
    context.chat_data["users"].update({"username": name})
    context.chat_data["users"].update({"userdata": answer})
    context.bot.send_message(chat_id=update.effective_chat.id, text=answer)
    context.dispatcher


def get_command(update, context):
    chat_id = update.effective_chat.id
    name = update.effective_user.first_name
    context.bot.send_message(chat_id=update.effective_chat.id, text="This is your data:")
    context.bot.send_message(chat_id=update.effective_chat.id, text=context.chat_data)


def read_list():
    return {k.strip(): int(v) for k, v in (l.split('=') for l in open("list.txt"))}


def play(user_id, group_id, user_name, value, update: Update) -> None:
    query = {'id': user_id, 'group_id': group_id,  'name': user_name, 'playValue': value}
    response = requests.get("http://127.0.0.1:8080/players/play", params=query)
    print("Response: "+response.text)
    response_object = json.loads(response.text)
    #response.json()
    user_name = response_object['name']
    user_score = response_object['points']
    if response_object['win']:
        if user_score > 1:
            update.message.reply_text(
                "GZ {}. Now you have {} points.".format(user_name, user_score))
        else:
            update.message.reply_text("GZ {}. Now you have {} point.".format(user_name, user_score))
    del user_id
    del user_name
    del value


def check_msg(update: Update, context: CallbackContext) -> None:
    """win values: [22,64,43,1]"""
    if (update.message.dice.value in range(100) and (
            '\U0001F3B0' == update.message.dice.emoji)):  # (update.message.dice.emoji).encode('utf-8')==b'\xf0\x9f\x8e\xb0'):
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        value = update.message.dice.value
        group_id = update.effective_chat.id
        play(user_id, group_id, user_name, value, update)
    del user_id
    del user_name


def read_token():
    f = open("token.txt", "r")
    token = str(f.readline()).strip()
    return token


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    # db_persistence = PsqlPersistence()
    updater = Updater(read_token(), use_context=True)
    session = requests.Session()
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("leaderboard", start, ~Filters.update.edited_message))
    dispatcher.add_handler(CommandHandler("points", start, ~Filters.update.edited_message))
    dispatcher.add_handler(CommandHandler("help", help_command, ~Filters.update.edited_message))
    dispatcher.add_handler(CommandHandler("test", test_command, ~Filters.update.edited_message))
    dispatcher.add_handler(CommandHandler('set', set_command))
    dispatcher.add_handler(CommandHandler('get', get_command))
    # the actual messages to reply to
    dispatcher.add_handler(MessageHandler(
        Filters.dice.slot_machine & ~Filters.command & ~Filters.forwarded,
        check_msg))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
