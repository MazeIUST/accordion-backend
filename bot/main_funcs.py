from datetime import datetime
from urllib import response
from telegram import (Update,
                      ParseMode,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton)
from telegram.ext import (Updater,
                          CommandHandler,
                          MessageHandler,
                          Filters,
                          CallbackContext,
                          CallbackQueryHandler,
                          ConversationHandler,)

from const import *
import requests
import os


def send_request(url, options):
    url = SERVER_URL + url + '/'
    for option in options:
        url += f'{option}/'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {'status': 'error'}


def cancel(update: Update, context: CallbackContext):
    """Cancels and ends the conversation."""
    update.message.reply_text(text='ended!')
    return ConversationHandler.END


def get_user_telegram_info_from_update(update: Update, context: CallbackContext):
    result = {}
    if update.callback_query:
        update = update.callback_query
        result['is_callback'] = True
    else:
        result['is_callback'] = False
    result['chat_id'] = update.message.chat_id
    result['first_name'] = update.message.from_user['first_name']
    result['last_name'] = update.message.from_user['last_name']
    result['username'] = update.message.from_user['username']
    result['is_group'] = update.message.chat.type != "private"
    result['language_code'] = update.message.from_user['language_code']
    return result


def download_song(song_link):
    song_id = song_link.split('/')[-2]
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_address = os.path.join(current_dir, 'songs', f'{song_id}.mp3')
    if os.path.exists(file_address):
        with open(file_address, 'rb') as song:
            return song.name
    song_link = f'https://drive.google.com/u/0/uc?id={song_id}&export=download'
    response = requests.get(song_link)
    with open(file_address, 'wb') as song:
        song.write(response.content)
    return song.name
