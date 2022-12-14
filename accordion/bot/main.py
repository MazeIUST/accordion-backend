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

PORT = int(os.environ.get('PORT', 5000))

def main():
    TOKEN = "5659133746:AAFQ7yYYMdBCNYwvA3-YSssaJXiNeyAs4Eg"
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # handlers
    start_handler = CommandHandler('start', start)
    search_handler = MessageHandler(Filters.text, search)

    # add handlers to dispatcher
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(search_handler)

    # updater.start_polling()
    updater.start_webhook(listen="0.0.0.0",
                            port=int(PORT),
                            url_path=TOKEN)
    updater.bot.setWebhook('https://accordion.herokuapp.com/' + TOKEN)
    updater.idle()


if __name__ == '__main__':
    main()