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
from flask import Flask, jsonify, request

app = Flask(__name__)



@app.route("/", methods=['GET', 'POST'])
def main():
    updater = Updater("5659133746:AAFQ7yYYMdBCNYwvA3-YSssaJXiNeyAs4Eg", use_context=True)
    dispatcher = updater.dispatcher

    # handlers
    start_handler = CommandHandler('start', start)
    search_handler = MessageHandler(Filters.text, search)

    # add handlers to dispatcher
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(search_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
    app.run(debug=True)
