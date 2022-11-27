
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
    response = send_request('start_bot', [user_info['chat_id']])
    if response['status'] == 'authenticated':
        return show_my_playlists(update, context)
    elif response['status'] == 'not_authenticated':
        signup_url = f'{SERVER_URL}/bot/signup/{user_info["chat_id"]}/'
        update.message.reply_text(RESPONSE_TEXTS['welcom'])
        update.message.reply_text(RESPONSE_TEXTS['signup'].format(signup_url), parse_mode=ParseMode.HTML)
        return ConversationHandler.END


def show_my_playlists(update: Update, context: CallbackContext):
    user_info = get_user_telegram_info_from_update(update, context)
    response = send_request('get_my_playlists', [user_info['chat_id']])
    if response['status'] == 'OK':
        playlists = response['playlists']
        if len(playlists) == 0:
            update.message.reply_text(RESPONSE_TEXTS['no_playlist'])
            return ConversationHandler.END
        else:
            update.message.reply_text(RESPONSE_TEXTS['my_playlists'])
            for playlist in playlists:
                update.message.reply_text(playlist['name'])
            return ConversationHandler.END
    else:
        update.message.reply_text(RESPONSE_TEXTS['error'])
        return ConversationHandler.END


