
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

USERS_KEYBOARD = {}


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
    user_songs = USERS_KEYBOARD.get(user_info['chat_id'])
    if user_songs:
        if text in user_songs:
            return get_song(update, context, user_songs[text])
    response = send_request('search', [text])
    if response:
        keyboard = []
        USERS_KEYBOARD[user_info['chat_id']] = {}
        for song in response:
            song_text = f'🎵 {song["title"]} - {song["artist_name"]}'
            keyboard.append(
                [KeyboardButton(song_text, callback_data=song['id'])])
            USERS_KEYBOARD[user_info['chat_id']][song_text] = song['id']
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        update.message.reply_text('search results:', reply_markup=reply_markup)
    else:
        update.message.reply_text('not found!')


def get_song(update: Update, context: CallbackContext, song_id=None):
    user_info = get_user_telegram_info_from_update(update, context)
    if not song_id:
        song_id = USERS_KEYBOARD.get(user_info['chat_id']).get(update.message.text)
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
    if response.get('status') == 'OK':
        keyboard = []
        USERS_KEYBOARD[user_info['chat_id']] = {}
        for playlist in response['playlists']:
            playlist_text = f'📀 {playlist["title"]}'
            keyboard.append(
                [KeyboardButton(playlist_text, callback_data=playlist['id'])])
            USERS_KEYBOARD[user_info['chat_id']
                           ][playlist_text] = playlist['id']
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        update.message.reply_text('playlists:', reply_markup=reply_markup)
        return GET_PLAYLIST


def get_playlist(update: Update, context: CallbackContext):
    user_info = get_user_telegram_info_from_update(update, context)
    text = update.message.text
    user_playlists = USERS_KEYBOARD.get(user_info['chat_id'])
    response = send_request(
        'get_playlist', [user_info['chat_id'], user_playlists[text]])
    if response.get('status') == 'OK':
        if not response['songs']:
            update.message.reply_text('playlist is empty!')
            return GET_PLAYLIST
        keyboard = []
        USERS_KEYBOARD[user_info['chat_id']] = {}
        for song in response['songs']:
            song_text = f'🎵 {song["title"]} - {song["artist_name"]}'
            keyboard.append(
                [KeyboardButton(song_text, callback_data=song['id'])])
            USERS_KEYBOARD[user_info['chat_id']][song_text] = song['id']
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        update.message.reply_text('playlist songs:', reply_markup=reply_markup)
        return GET_SONG
    else:
        update.message.reply_text(RESPONSE_TEXTS['error'])
        return GET_PLAYLIST
    
def song_analysis(update: Update, context: CallbackContext):
    user_info = get_user_telegram_info_from_update(update, context)
    response = send_request('song_analysis', [user_info['chat_id']]) 
    if response.get('status') == 'OK':
        datas = response.get('data')
        values = [data['percent'] for data in datas]
        keys = [data['name'] for data in datas]
        # show chart with matplotlib
        import matplotlib.pyplot as plt
        import numpy as np

        y = np.array(values)
        mylabels = keys

        plt.pie(y, labels = mylabels)
        plt.savefig('piechart.jpg')
        
        update.message.reply_photo(photo=open('piechart.jpg', 'rb'))
        return ConversationHandler.END
    else:
        update.message.reply_text(RESPONSE_TEXTS['error'])
        return ConversationHandler.END
        

    
