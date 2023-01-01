
import keyword
from telegram import (Update,
                      ParseMode,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton,
                      KeyboardButton,
                      ReplyKeyboardMarkup)
from telegram.ext import (Updater,
                          CommandHandler,
                          MessageHandler,
                          Filters,
                          CallbackContext,
                          CallbackQueryHandler,
                          ConversationHandler,)

from const import *
from main_funcs import *

USERS_SERACH_KEYBOARD = {}


def start(update: Update, context: CallbackContext):
    user_info = get_user_telegram_info_from_update(update, context)
    response = send_request('start', [user_info['chat_id']])
    if response['status'] == 'OK':
        update.message.reply_text(RESPONSE_TEXTS['help'])
        return ConversationHandler.END
    else:
        update.message.reply_text(RESPONSE_TEXTS['welcom'])
        return GET_USERPASS


def get_userpass(update: Update, context: CallbackContext):
    user_info = get_user_telegram_info_from_update(update, context)
    userpass = update.message.text
    if len(userpass.split('\n')) != 2:
        update.message.reply_text(RESPONSE_TEXTS['userpass_error_2_lines'])
        return GET_USERPASS
    username = userpass.split('\n')[0]
    password = userpass.split('\n')[1]
    response = send_request(
        'login', [user_info['chat_id'], username, password])
    if response.get('status') == 'OK':
        update.message.reply_text(RESPONSE_TEXTS['userpass_correct'])
        update.message.reply_text(RESPONSE_TEXTS['help'])
        return ConversationHandler.END
    else:
        update.message.reply_text(RESPONSE_TEXTS['userpass_wrong'])
        return GET_USERPASS


def search(update: Update, context: CallbackContext):
    user_info = get_user_telegram_info_from_update(update, context)
    text = update.message.text
    user_songs = USERS_SERACH_KEYBOARD.get(user_info['chat_id'])
    if user_songs:
        if text in user_songs:
            return get_song(update, context, user_songs[text])
    response = send_request('search', [text])
    if response:
        keyboard = []
        USERS_SERACH_KEYBOARD[user_info['chat_id']] = {}
        for song in response:
            song_text = f'🎵 {song["title"]} - {song["artist_name"]}'
            keyboard.append(
                [KeyboardButton(song_text, callback_data=song['id'])])
            USERS_SERACH_KEYBOARD[user_info['chat_id']][song_text] = song['id']
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        update.message.reply_text('search results:', reply_markup=reply_markup)
    else:
        update.message.reply_text('not found!')


def get_song(update: Update, context: CallbackContext, song_id):
    user_info = get_user_telegram_info_from_update(update, context)
    response = send_request('get_song', [song_id])
    if response.get('status') == 'OK':
        song_link = response.get('song').get('song_link')
        message_id = update.message.reply_text('downloading...').message_id
        song_name = download_song(song_link)
        # send song and delete message
        update.message.bot.edit_message_text(
            'sending...', chat_id=user_info['chat_id'], message_id=message_id)
        update.message.reply_audio(audio=open(song_name, 'rb'))
        update.message.bot.delete_message(
            chat_id=user_info['chat_id'], message_id=message_id)
    else:
        update.message.reply_text(RESPONSE_TEXTS['error'])

    return ConversationHandler.END


def my_playlists(update: Update, context: CallbackContext):
    user_info = get_user_telegram_info_from_update(update, context)
    response = send_request('get_playlists', [user_info['chat_id']])
    print(response.get('status'))
    if response.get('status') == 'OK':
        keyboard = []
        for playlist in response['playlists']:
            keyboard.append(
                [KeyboardButton(playlist['title'], callback_data=playlist['id'])])
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        update.message.reply_text('your playlists:', reply_markup=reply_markup)
    else:
        update.message.reply_text('not found!')
