#!/usr/bin/env python
# required packages:
# apt-get install python3-paho-mqtt

import paho.mqtt.client as mqtt
import json
import os
import logging
from threading import Thread
import requests
import re
import os.path
from os import path
from deezloader.deezloader import DeeLogin


client = mqtt.Client("mqtt-ha")


def sanitize(value):
    invalid = '<>:"/\|?*&'
    for char in invalid:
        value = value.replace(char, '')
    return value

def send_message(uid, code, message):
    message = { 'uid': uid, 'code': code, 'message': message }
    client.publish("/music/download/progress", json.dumps(message))

def get_track_file(quality, artist, title, isrc):
    if quality == 'MP3_128':
        return f'{title} - {artist} [{isrc}] (128).mp3'
    elif quality == 'MP3_320':
        return f'{title} - {artist} [{isrc}] (320).mp3'
    else:
        return f'{title} - {artist} [{isrc}].flac'

def get_extension(quality):
    return '.mp3' if (quality == 'MP3_128' or quality == 'MP3_320') else '.flac'

def get_base_directory(quality):
    return f'format_{quality.lower()}'

# Get album information from deezer
def get_deezer_album_info(album):
    response = requests.get(f'https://api.deezer.com/album/{album}').json()
    album_name = sanitize(response['title'])
    artist = sanitize(response['artist']['name'])
    upc = response['upc']
    cover_url = response['cover_xl']
    tracks = []
    for track in response['tracks']['data']:
        tracks.append(track['id'])
    return (artist, album_name, tracks, upc, cover_url)

# Get track info form deezer
def get_deezer_track_info(track):
    response = requests.get(f'https://api.deezer.com/track/{track}').json()
    contributors = []
    for c in response['contributors']:
        contributors.append(sanitize(c['name']))        
    return (response['track_position'], sanitize(response['title']), "  ".join(contributors), response['isrc'])


# Download cover image from deezer
def download_deezer_cover(cover_url, destination_folder, uid):
    img_response = requests.get(cover_url)
    if img_response.ok:
        with open(f'{destination_folder}/cover.jpg', 'wb') as f:
            f.write(img_response.content)


def download_deezer_track(track, quality, arl):
    downloader = DeeLogin(arl=arl)
    downloader.download_trackdee(
        f'https://www.deezer.com/en/track/{track}',
        output_dir = './Songs',
        quality_download = quality,
        recursive_quality = False,
        recursive_download = False,
        method_save = 2
    )

def download_album_from_deezer(url, quality, uid):
    arl = os.getenv("ARL_COOKIE")
    match = re.search(r"https:\/\/.*\/album\/(\d+)", url)
    album = match.group(1)
    artist, album_name, tracks, upc, cover_url = get_deezer_album_info(album)

    deezer_dw_dir = f'./Songs/{album_name} - {artist} [{upc}]'
    normalized_dir = f'./Songs/{get_base_directory(quality)}/{artist}/{album_name}'

    send_message(uid, 'progress', f'** Descargando {album_name} - {artist} **')

    # Create directory if not exists
    if not os.path.isdir(f'{normalized_dir}'):
        os.makedirs(f'{normalized_dir}')
    
    # Download album cover
    if not path.exists(f'{normalized_dir}/cover.jpg'):
        download_deezer_cover(cover_url, f'{normalized_dir}', uid)

    # Download tracks and rename
    for track in tracks:
        nro, title, contributors, isrc = get_deezer_track_info(track)
        deezer_file_name = f'{deezer_dw_dir}/{get_track_file(quality, contributors, title, isrc)}'
        # TODO verificar que el nombre tenga el formato correcto
        filename = f'{str(nro).zfill(2)} - {title}{get_extension(quality)}'
        if not path.exists(f'{normalized_dir}/{filename}'):
            if not path.exists(f'{deezer_file_name}'):
                send_message(uid, 'progress', f'Downloading {filename} ...')
                try:
                    download_deezer_track(track, quality, arl)
                    os.rename(deezer_file_name, f'{normalized_dir}/{filename}')
                    send_message(uid, 'progress', f'{filename} ✓')
                except: 
                    send_message(uid, 'progress', f'{filename} ✗')
            else:
                os.rename(deezer_file_name, f'{normalized_dir}/{filename}')
                send_message(uid, 'progress', f'{filename} ✓')
        else:
            if path.exists(f'{deezer_file_name}'):
                os.remove(deezer_file_name)
            send_message(uid, 'progress', f'{filename} ✓')
    
    if path.exists(deezer_dw_dir):
        os.rmdir(deezer_dw_dir)
    send_message(uid, 'progress', 'Done')
        

def on_download_message(payload):
    url=payload['url']
    quality=payload['quality']
    uid=payload['uid']
    if url.startswith('https://www.deezer.com'):
        logging.info(f'Downloading album {url} from deezer')
        thread = Thread(target=download_album_from_deezer, args=(url,quality, uid))
        thread.start()
    else:
        logging.error('url not recognized')
        response = { 'message': 'url not recognized', 'code': 'error' }
        client.publish("/music/download/progress", json.dumps(response))


def on_message(mclient, userdata, message):
    payload = json.loads(str(message.payload.decode("utf-8","ignore")))
    on_download_message(payload)

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, encoding='utf-8', level=logging.INFO, datefmt="%H:%M:%S")

    try:
        mqtt_host = os.getenv("MQTT_HOST")
        mqtt_user = os.getenv("MQTT_USER")
        mqtt_pass = os.getenv("MQTT_PASS")

        client.username_pw_set(mqtt_user, mqtt_pass)
        client.connect(mqtt_host)
        client.subscribe("/music/download")
        client.on_message=on_message
        client.loop_forever()
    except:
        logging.error("failed to connect, moving on")