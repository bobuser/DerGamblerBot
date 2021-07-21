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

import prettytable as pt
import requests
import imgkit
from telegram import Update, bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
from configReader import config

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

params = config()
ENDPOINT_URL = params["host"] + ":" + params["port"]


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text("👋")


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    table = pt.PrettyTable(['Commands', 'Use'])
    table.align['Commands'] = 'l'
    table.align['Use'] = 'l'
    data = [
        ('/cash', 'See your cash'),
        ('/help', 'This!'),
        ('/leaderboard', 'Overall scores in the group'),
        ('/points', 'same as /leaderboard'),
        ('/name', 'Change your display name'),
        ('/whoami', 'Show your current name'),
        ('/commands', 'Shows a clickable list of comms')
    ]
    for commands, use in data:
        table.add_row([commands, use])
    options = {
        'format': 'png',
        'crop-w': 450,
        'encoding': "UTF-8"
    }

    img = imgkit.from_string(f'<pre>{table}</pre>', 'help.png', options=options)
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('help.png', 'rb'))
    # update.message.reply_text(f'```{table}```', parse_mode='MarkdownV2')
    del data


def set_name_command(update, context):
    if len(context.args) < 1:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide a new name after '/name'.")
        return
    answer = ' '.join(context.args)
    player_id = update.effective_user.id
    group_id = update.effective_chat.id
    query = {'playerId': player_id, 'groupId': group_id, 'newName': answer}
    response = requests.get(ENDPOINT_URL + "/players/changeName", params=query)
    context.bot.send_message(chat_id=update.effective_chat.id, text="From now on I will call you {}".format(answer))


def get_name_command(update, context):
    player_id = update.effective_user.id
    group_id = update.effective_chat.id
    query = {'playerId': player_id, 'groupId': group_id}
    response = requests.get(ENDPOINT_URL + "/players/check", params=query)
    response = response.json()
    response = response['name']
    context.bot.send_message(chat_id=update.effective_chat.id, text="You are {}".format(response))
    del player_id
    del group_id
    del response


def play(player_id, group_id, user_name, value, update: Update) -> None:
    query = {'playerId': player_id, 'groupId': group_id, 'name': user_name, 'playValue': value}
    response = requests.get(ENDPOINT_URL + "/players/play", params=query)
    print("Response: " + response.text)
    response_object = response.json()
    user_name = response_object['name']
    user_score = response_object['points']
    if response_object['customResponse']:
        update.message.reply_text(response_object['customResponse'])
    if response_object['win']:
        if response_object['customResponse']:
            update.message.reply_text(response_object['customResponse'])
        else:
            if user_score > 1:
                update.message.reply_text(
                    "GZ {}. Now you have {} points. +20 Cash".format(user_name, user_score))
            else:
                update.message.reply_text("GZ {}. Now you have {} point. +20 Cash".format(user_name, user_score))
    del player_id
    del group_id
    del user_name
    del value


def cash_command(update: Update, context: CallbackContext) -> None:
    player_id = update.effective_user.id
    group_id = update.effective_chat.id
    query = {'playerId': player_id, 'groupId': group_id}
    response = requests.get(ENDPOINT_URL + "/players/check", params=query)
    response_object = response.json()
    update.message.reply_text(
        "You have {:.2f} cash and {} point(s).".format(response_object['cash'], response_object['points']))
    del player_id
    del group_id


def comm_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('My commands are:\r\n/cash\r\n/help\r\n/leaderboard\r\n/points\r\n/name\r\n/whoami')


def take_second(elem):
    return elem[1]


def leaderboard_command(update: Update, context: CallbackContext) -> None:
    group_id = update.effective_chat.id
    query = {'groupId': group_id}
    response = requests.get(ENDPOINT_URL + "/players/leaderboard", params=query)
    print("Response: " + response.text)
    response_object = response.json()

    table = pt.PrettyTable(['Name', 'Points', 'Cash'])
    table.align['Name'] = 'l'
    table.align['points'] = 'r'
    table.align['Cash'] = 'r'
    data = []
    for item in response_object:
        short_name = item['name']
        short_name = short_name[:8]
        data.append((short_name, item['points'], item['cash']))
        print(data)
    data.sort(key=take_second, reverse=True)
    for name, points, cash in data:
        table.add_row([name, f'{points:}', f'{cash:.2f}'])
    options = {
        'format': 'png',
        'crop-w': 350,
        'encoding': "UTF-8"
    }

    img = imgkit.from_string(f'<pre>{table}</pre>', 'out.png', options=options)
    # img_string = f'<pre>{table}</pre>'
    # HTML(string=img_string).write_png(target='out.png')
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('out.png', 'rb'))
    # update.message.reply_text(f'```{table}```', parse_mode='MarkdownV2')
    del data
    del group_id
    del img


def pic_command(update: Update, context: CallbackContext) -> None:
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('DSC07614.JPG', 'rb'))


def check_msg(update: Update, context: CallbackContext) -> None:
    """win values: [22,64,43,1]"""
    if (update.message.dice.value in range(100) and (
            '\U0001F3B0' == update.message.dice.emoji)):  # (update.message.dice.emoji).encode('utf-8')==b'\xf0\x9f\x8e\xb0'):
        player_id = update.effective_user.id
        user_name = update.effective_user.first_name
        value = update.message.dice.value
        group_id = update.effective_chat.id
        play(player_id, group_id, user_name, value, update)
    del player_id
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

    updater = Updater(read_token(), use_context=True)
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start, ~Filters.update.edited_message))
    dispatcher.add_handler(CommandHandler("leaderboard", leaderboard_command, ~Filters.update.edited_message))
    dispatcher.add_handler(CommandHandler("points", leaderboard_command, ~Filters.update.edited_message))
    dispatcher.add_handler(CommandHandler("help", help_command, ~Filters.update.edited_message))
    dispatcher.add_handler(CommandHandler("cash", cash_command, ~Filters.update.edited_message))
    dispatcher.add_handler(CommandHandler("pic", pic_command, ~Filters.update.edited_message))
    dispatcher.add_handler(CommandHandler("commands", comm_command, ~Filters.update.edited_message))
    dispatcher.add_handler(CommandHandler('name', set_name_command))
    dispatcher.add_handler(CommandHandler('whoami', get_name_command))
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
