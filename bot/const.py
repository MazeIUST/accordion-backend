TOKEN = "5659133746:AAFQ7yYYMdBCNYwvA3-YSssaJXiNeyAs4Eg"
SONGS_CHANNEL = "@accordion_songs"

GET_USERPASS = 'get_userpass'
GET_PLAYLIST = 'get_playlist'
GET_SONG = 'get_song'

# SERVER_URL = 'http://127.0.0.1:8000/bot/'
SERVER_URL = 'https://accordion2.pythonanywhere.com/bot/'
CLOUD_SERVER_URL = 'https://accordioncloud.pythonanywhere.com/cloud/'

RESPONSE_TEXTS = {
    'error': 'something went wrong!',
    'welcom': 'Hi.\nPlease send your username and password in one message and in two lines.',
    'signup': '{}',
    'userpass_error_2_lines': 'Please send your username and password in one message and in two lines.',
    'userpass_correct': 'login successfull.',
    'userpass_wrong': 'Username or password is wrong.\nPlease send your username and password in one message and in two lines.',
    'help': 'for search send your text:',
    'song_added': 'song added!',
}
