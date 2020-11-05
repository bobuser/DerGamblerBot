#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, PicklePersistence

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    output=""
    for user in context.chat_data.values():
      output=output+"{} : {} ".format(user.get("name"),user.get("score"))
    update.message.reply_text(output)


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message. [22,64,43,1]"""
    if(update.message.dice.value in [22,64,43,1] and ('\U0001F3B0'==update.message.dice.emoji)): #(update.message.dice.emoji).encode('utf-8')==b'\xf0\x9f\x8e\xb0'):
      user_id=update.effective_user.id
      name=update.effective_user.first_name
      print(context.chat_data)
      if(not user_id in context.chat_data):
        context.chat_data[user_id] = {"name": name, "score" : 0}
        print(context.chat_data)
        if(user_id==436304467): context.chat_data[user_id].update({"score" : 99})
      else:
        context.chat_data[user_id].update({"name": name})
      if(context.chat_data.get(user_id) and context.chat_data.get(user_id).get("score")):
        context.chat_data[user_id]["score"] = context.chat_data[user_id]["score"]+1
        update.message.reply_text("GZ {}. Now you have {} points.".format(update.message.from_user.first_name, context.chat_data[user_id]["score"]))
      else:
        if(not context.chat_data):
          context.chat_data[user_id].update({"score" : 1})
        else:
          context.chat_data[user_id].update({"score" : 1})
        update.message.reply_text("GZ {}. Now you have {} point.".format(update.message.from_user.first_name, context.chat_data[user_id]["score"]))
    print(context.chat_data)
    #del user_id


def main():
    pp = PicklePersistence(filename='gamblebot')
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("TOKEN", persistence=pp, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("leaderboard", start))
    dispatcher.add_handler(CommandHandler("points", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on noncommand i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.dice & ~Filters.command & ~Filters.forwarded & ~Filters.dice.darts & ~Filters.dice.basketball & ~Filters.dice.dice, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
