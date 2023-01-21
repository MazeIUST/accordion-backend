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


def send_request(url, options, server_url=SERVER_URL):
    url = server_url + url + '/'
    for option in options:
        url += f'{option}/'
    response = requests.get(url)
    if response.status_code in [200, 201]:
        return response.json() + {'status': 'OK'}
    else:
        return {'status': 'error'}


def send_post_request(url, datas=None, files=None, server_url=SERVER_URL):
    url = server_url + url + '/'
    response = requests.post(url, data=datas, files=files)
    if response.status_code in [200, 201]:
        return response.json()
    else:
        return {'status': 'error', 'message': response.text}


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


def get_song_info(update: Update, context: CallbackContext):
    song = update.message.audio
    if song:
        try:
            id = song.file_id
            title = song.title
            artist = song.performer
            image = song.thumb.file_id
        except:
            return None
        # create images folder if not exists
        images_dir = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'images')
        if not os.path.exists(images_dir):
            os.mkdir(images_dir)
        # save image
        image_path = os.path.join(images_dir, f'{image}.jpg')
        image_file = context.bot.get_file(image)
        image_file.download(image_path)
        # forward to channel
        forwarded_song = context.bot.forward_message(chat_id=SONGS_CHANNEL, from_chat_id=update.message.chat_id,
                                                     message_id=update.message.message_id)
        data = {'id': id, 'title': title,
                'artistic_name': artist, 'telegram_id': forwarded_song.message_id}
        files = {'image': open(image_path, 'rb')}
        return {'data': data, 'files': files, 'song': song}
    return None


def download_song(song_link):
    song_id = song_link.split('/')[-2]
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_address = os.path.join(current_dir, 'songs', 'song.mp3')
    new_song_link = f'https://drive.google.com/u/0/uc?id={song_id}&export=download'
    try:
        response = requests.get(song_link)
    except:
        response = requests.get(new_song_link)
    with open(file_address, 'wb') as song:
        song.write(response.content)
    return song.name


def upload_to_cloud(song, context: CallbackContext):
    # download song from telegram
    current_dir = os.path.dirname(os.path.abspath(__file__))
    songs_dir = os.path.join(current_dir, 'songs')
    if not os.path.exists(songs_dir):
        os.mkdir(songs_dir)
    song_path = os.path.join(songs_dir, 'song.mp3')
    song_file = context.bot.get_file(song)
    song_file.download(song_path)

    # upload to cloud
    response = send_post_request('add_song', files={'file': open(
        song_path, 'rb')}, server_url=CLOUD_SERVER_URL)
    # delete song
    os.remove(song_path)
    if response.get('status') != 'error':
        song_link = response['song_link']
        return song_link
    else:
        return None
