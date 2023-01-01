from telegram.ext import (Updater,
                          CommandHandler,
                          MessageHandler,
                          Filters,
                          CallbackContext,
                          CallbackQueryHandler,
                          ConversationHandler,)
from start import *
from const import *
from main_funcs import *
import os

# PORT = int(os.environ.get('PORT', 8443))

def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # handlers
    start_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            GET_USERPASS: [MessageHandler(Filters.text, get_userpass)],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    search_handler = MessageHandler(Filters.text, search)
    # command_handler = MessageHandler(Filters.command, command)
    playlist_handler = CommandHandler('my_playlists', my_playlists)

    # add handlers to dispatcher
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(search_handler)
    # dispatcher.add_handler(command_handler)
    dispatcher.add_handler(playlist_handler)

    updater.start_polling()
    # updater.start_webhook(listen="0.0.0.0",
    #                         port=PORT,
    #                         url_path=TOKEN)
    # updater.bot.setWebhook('https://accordion.herokuapp.com/' + TOKEN)
    updater.idle()


if __name__ == '__main__':
    main()