
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
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

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
    if type(response) == list:
        keyboard = []
        USERS_KEYBOARD[user_info['chat_id']] = {}
        for song in response:
            song_text = f'🎵 {song["title"]} - {song["artist_name"]}'
            keyboard.append(
                [KeyboardButton(song_text, callback_data=song['id'])])
            USERS_KEYBOARD[user_info['chat_id']][song_text] = song['id']
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        if keyboard:
            update.message.reply_text(
                'search results:', reply_markup=reply_markup)
        else:
            update.message.reply_text('not found!')
    else:
        update.message.reply_text('not found!')


def get_song(update: Update, context: CallbackContext, song_id=None):
    user_info = get_user_telegram_info_from_update(update, context)
    if not song_id:
        song_id = USERS_KEYBOARD.get(
            user_info['chat_id']).get(update.message.text)
    response = send_request('get_song', [song_id])
    if response.get('status') == 'OK':
        telegram_id = response.get('song').get('telegram_id')
        if telegram_id:
            # forward from channel
            update.message.bot.forward_message(
                chat_id=user_info['chat_id'],
                from_chat_id=SONGS_CHANNEL,
                message_id=telegram_id)
            return ConversationHandler.END
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
        if keyboard:
            update.message.reply_text('playlists:', reply_markup=reply_markup)
            return GET_PLAYLIST
        else:
            update.message.reply_text('you have no playlists!')
            return ConversationHandler.END
    else:
        update.message.reply_text(RESPONSE_TEXTS['error'])
        return ConversationHandler.END


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


def remove_zero_count(datas):
    return [data for data in datas if data['count'] != 0]


def song_analysis(update: Update, context: CallbackContext):
    update.message.reply_text('wait...')
    user_info = get_user_telegram_info_from_update(update, context)
    response = send_request('analysis_song', [user_info['chat_id']])
    if response.get('status') == 'OK':
        by_tags = remove_zero_count(response.get('by_tags'))
        by_artist = remove_zero_count(response.get('by_artist'))
        by_top_songs = remove_zero_count(response.get('by_top_songs'))
        by_last_songs = remove_zero_count(response.get('by_last_songs'))
        analysis = {
            'analysis by tags': by_tags,
            'analysis by artist': by_artist,
        }
        artist_analysis = {
            'analysis by top songs': by_top_songs,
            'analysis by last songs': by_last_songs
        }
        # remove empty analysis
        analysis = {k: v for k, v in analysis.items() if v}

        figs, axis = plt.subplots(1, 2)
        for i, (key, value) in enumerate(analysis.items()):
            keys = [v['name'] for v in value]
            values = [v['count'] for v in value]
            axis[i].set_title(key)
            axis[i].pie(values, labels=keys)
        figs.set_size_inches(18.5, 10.5)
        figs.savefig('user_analysis.png')

        figs, axis = plt.subplots(1, 2)
        for i, (key, value) in enumerate(artist_analysis.items()):
            keys = [v['name'] for v in value]
            values = [v['count'] for v in value]
            axis[i].set_title(key)
            axis[i].pie(values, labels=keys)
        figs.set_size_inches(18.5, 10.5)
        figs.savefig('artist_analysis.png')
        update.message.reply_photo(photo=open('user_analysis.png', 'rb'))
        update.message.reply_photo(photo=open(
            'artist_analysis.png', 'rb')) if by_top_songs else None

    else:
        update.message.reply_text(RESPONSE_TEXTS['error'])
        return ConversationHandler.END


def add_new_song(update: Update, context: CallbackContext):
    message = update.message.reply_text('downloading...')
    song = get_song_info(update, context)
    if song:
        song_link = upload_to_cloud(song['song'], context)
        song['data']['song_link'] = song_link
        response = send_post_request('add_song', song['data'], song['files'])
        if response.get('status') == 'OK':
            message.edit_text(RESPONSE_TEXTS['song_added'])
        else:
            message.edit_text(response.get('message'))
    else:
        message.edit_text(RESPONSE_TEXTS['error'])
