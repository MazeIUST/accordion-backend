
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
from main_funcs import *

def start(update: Update, context: CallbackContext):
    user_info = get_user_telegram_info_from_update(update, context)
    response = send_request('start', [user_info['chat_id']])
    if response['status'] == 'authenticated':
        return show_my_playlists(update, context)
    else:
        signup_url = f'{SERVER_URL}signup/{user_info["chat_id"]}/'
        update.message.reply_text(RESPONSE_TEXTS['welcom'])
        update.message.reply_text(RESPONSE_TEXTS['signup'].format(signup_url), parse_mode=ParseMode.HTML)
        return ConversationHandler.END


def show_my_playlists(update: Update, context: CallbackContext):
    user_info = get_user_telegram_info_from_update(update, context)
    response = send_request('get_my_playlists', [user_info['chat_id']])
    if response['status'] == 'OK':
        song_link = response['song']
        # download song
        song_name = download_song(song_link)
        # send song
        print(song_name)
        update.message.reply_audio(audio=open(song_name, 'rb'))
    else:
        update.message.reply_text(RESPONSE_TEXTS['error'])
        
    return ConversationHandler.END

def search(update: Update, context: CallbackContext):
    user_info = get_user_telegram_info_from_update(update, context)
    response = send_request('search', [user_info['chat_id'], update.message.text])
    if response['status'] == 'OK':
        for song in response['songs']:
            update.message.reply_text(song['name'])
    else:
        update.message.reply_text('error')


        


