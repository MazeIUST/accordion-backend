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




def main():
    updater = Updater("5659133746:AAFQ7yYYMdBCNYwvA3-YSssaJXiNeyAs4Eg", use_context=True)
    dispatcher = updater.dispatcher

    # handlers
    start_handler = CommandHandler('start', start)

    # add handlers to dispatcher
    dispatcher.add_handler(start_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()