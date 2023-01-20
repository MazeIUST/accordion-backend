from Google import Create_Service
from googleapiclient.http import MediaFileUpload
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRET_FILE = os.path.join(current_dir, 'client_secrets.json')
API_NAME = 'drive'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/drive']

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

folder_id = '1niLMRkf31NyU7rbtCznPoln03zsxj4Kr'
file_metadata = {
    'name': 'song.mp3',
    'parents': [folder_id]
}
songs_dir = os.path.join(current_dir, 'songs')
song_path = os.path.join(songs_dir, 'song.mp3')
media = MediaFileUpload(song_path, mimetype='audio/mp3')
file = service.files().create(
    body=file_metadata,
    media_body=media,
    fields='id'
).execute()
id = file.get('id')
song_link = f'https://drive.google.com/file/d/{id}/view?usp=drivesdk'
print(song_link)
