#!/usr/bin/env python
# required packages:
# apt-get install python3-paho-mqtt

import paho.mqtt.client as mqtt
import json
import os
import logging
from threading import Thread
import re
import math
import os.path
from os import path

from deezer_utils import *

mqtt_host = os.getenv("MQTT_HOST")
mqtt_user = os.getenv("MQTT_USER")
mqtt_pass = os.getenv("MQTT_PASS")
arl = os.getenv("ARL_COOKIE")

client = mqtt.Client("deezer-dw")


def send_message(uid, code, message, progress=0):
    message = { 'uid': uid, 'code': code, 'message': message, 'progress' : progress }
    client.publish("/music/download/progress", json.dumps(message))


def post_album_data(message):
    client.publish("/music/create/album", json.dumps(message))


def get_extension(quality):
    return '.mp3' if (quality == 'MP3_128' or quality == 'MP3_320') else '.flac'


def get_base_directory(quality):
    return f'format_{quality.lower()}'


def update_metadata(filename, artist, disk_number, multi_cd):
    if not path.exists(filename):
        return
    f = music_tag.load_file(filename)

    if multi_cd:
        f['discnumber'] = disk_number
    else:
        logging.info("Removing discnumber and totaldiscs tags")
        del f['totaldiscs']
        del f['discnumber']

    year_value = f['year'].value
    if (match := re.match(r"^([0-9]{4}).*", str(year_value))) is not None:
        year = match.group(1)
        f['year'] = year
        logging.info(f'Updating year to {year}')

    artist_value = f['albumartist'].value
    if artist_value != artist:
        logging.info(f'Updating albumartist to {artist}')
        f['albumartist'] = artist

    f['comment'] = ''
    f.save()


def create_directory(base_directory, artist, album_name, multi_cd, disk_number):
    if multi_cd:
        normalized_dir = f'./Songs/{base_directory}/{artist}/{album_name}/CD{disk_number}'
        if not os.path.isdir(normalized_dir):
            os.makedirs(normalized_dir)
        return normalized_dir
    else:
        normalized_dir = f'./Songs/{base_directory}/{artist}/{album_name}'
        if not os.path.isdir(normalized_dir):
            os.makedirs(normalized_dir)
        return normalized_dir


def download_album_from_deezer(url, quality, uid, arl):
    match = re.search(r"https:\/\/.*\/album\/(\d+)", url)
    album = match.group(1)
    artist, album_name, tracks, upc, cover_url, release_date = get_deezer_album_info(album)
    tracks_info, multi_cd = get_tracks_info(tracks)

    if (match := re.match(r"^([0-9]{4}).*", str(release_date))) is not None:
        year = match.group(1)
    else:
        year = None

    send_message(uid, 'progress', f'** Descargando {album_name} - {artist} **', 0)
    album_post_data = {
        'title': album_name,
        'artist': artist,
        'album_artist': artist,
        'upc': upc,
        'cover_url': cover_url,
        'format': quality,
        'source': 'DEEZER',
        'source_id': album,
        'year': year,
        'tracks': []
    }

    deezer_dw_dir = None
    # Download tracks and rename
    progress = 0
    total_tracks = len(tracks_info) + 1
    track_nro = 0
    for track in tracks_info:
        progress = math.floor(100 * (track_nro / total_tracks))
        track_id = track['id']
        nro = track['track']
        song_title = track['song_title']
        title_short = track['title_short']
        title_version = track['title_version']
        disk_number = track['disk_number']

        send_message(uid, 'progress', f'Downloading {title_short} ...', progress)
        try:
            track_result = download_deezer_track(track_id, quality, arl)
            if track_result.success:
                normalized_dir = create_directory(get_base_directory(quality), track_result.ar_album, album_name, multi_cd, disk_number)
                filename, full_name = get_full_name(normalized_dir, nro, quality, title_short)
                os.rename(track_result.song_path, full_name)
                update_metadata(full_name, track_result.artist, disk_number, multi_cd)
                send_message(uid, 'progress', f'{filename} ✓', progress)
                if deezer_dw_dir is None:
                    deezer_dw_dir = os.path.dirname(track_result.song_path)

                album_post_data['album_artist'] = track_result.ar_album
                track_data = {
                    'title': song_title,
                    'artist': track_result.artist,
                    'track_number': track_result.tracknum,
                    'disc_number': track_result.discnum,
                    'comments': title_version,
                    'media_url': full_name[7:],
                    'isrc': track_result.isrc,
                    'upc': track_result.upc,
                    'duration': track_result.duration
                }
                album_post_data['tracks'].append(track_data)

            else:
                send_message(uid, 'progress', f'{title_short} ✗', progress)
        except ValueError as err:
            print("Error descagando: ", err)
            logging.error("Error descargando", err)
            send_message(uid, 'progress', f'{title_short} ✗', progress)
        track_nro += 1

    if path.exists(deezer_dw_dir):
        os.rmdir(deezer_dw_dir)
    send_message(uid, 'progress', 'Done', 100)
    post_album_data(album_post_data)


def get_full_name(normalized_dir, nro, quality, title_short):
    filename = f'{str(nro).zfill(2)} - {title_short}{get_extension(quality)}'
    full_name = f'{normalized_dir}/{filename}'
    return filename, full_name


def on_download_message(payload):
    url = payload['url']
    quality = payload['quality']
    uid = payload['uid']
    if url.startswith('https://www.deezer.com'):
        logging.info(f'Downloading album {url} from deezer')
        thread = Thread(target=download_album_from_deezer, args=(url, quality, uid, arl))
        thread.start()
    else:
        logging.error('url not recognized')
        response = {'message': 'url not recognized', 'code': 'error'}
        client.publish("/music/download/progress", json.dumps(response))


def on_message(mclient, userdata, message):
    print("received message: ", str(message.payload.decode("utf-8")))
    payload = json.loads(str(message.payload.decode("utf-8","ignore")))
    on_download_message(payload)


if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, encoding='utf-8', level=logging.INFO, datefmt="%H:%M:%S")

    try:
        client.username_pw_set(mqtt_user, mqtt_pass)
        client.connect(mqtt_host)
        client.subscribe("/music/download")
        client.on_message = on_message
        client.loop_forever()
    except ValueError as ve:
        logging.error("failed to connect, moving on", ve)
