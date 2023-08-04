import sys
import getopt

import aigpy
import time

import urllib.request

from tidal_dl.events import *
from tidal_dl.settings import *
from tidal_dl.download import __encrypted__
from tidal_dl.download import __setMetaData__
from tidal_dl.download import __isSkip__


def init_tidal():
    SETTINGS.read(getProfilePath())
    TOKEN.read(getTokenPath())
    TIDAL_API.apiKey = apiKey.getItem(SETTINGS.apiKeyIndex)
    if not apiKey.isItemValid(SETTINGS.apiKeyIndex):
        changeApiKey()
        loginByWeb()
    elif not loginByConfig():
        loginByWeb()
    Printf.checkVersion()



class TidalTrackDownloadResult:
    def __init__(self, success, path):
        self.success = success
        self.path = path


def get_tidal_album_info(album_id):
    if aigpy.string.isNull(album_id):
        Printf.err('Please enter something.')
        return

    try:
        etype, obj = TIDAL_API.getByString(album_id)
        artist = obj.artist.name
        album_name = obj.title
        upc = ''
        cover_url = TIDAL_API.getCoverUrl(obj.cover, "1280", "1280")
        release_date = obj.releaseDate
        volumes = obj.numberOfVolumes
        return artist, album_name, upc, cover_url, release_date, volumes, obj
    except Exception as e:
        Printf.err(str(e) + " [" + album_id + "]")
        return


def get_tidal_tracks_info(album_id):
    tracks_info = []
    tracks, videos = TIDAL_API.getItems(album_id, Type.Album)
    for track in tracks:
        tracks_info.append({
            'id': track.id,
            'track': track.trackNumber,
            'title': track.title,
            'contributors': '',
            'isrc': track.isrc,
            'disk_number': track.volumeNumber,
            'api_track': track
        })
    return tracks_info


def create_directory(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directorio creado: {directory}")
    else:
        print("El directorio ya existe.")


def download_tidal_track(track, album):
    try:
        stream = TIDAL_API.getStreamUrl(track.id, SETTINGS.audioQuality)
        path = getTrackPath(track, stream, album, None)
        create_directory(path)

        if SETTINGS.showTrackInfo:
            Printf.track(track, stream)

        # check exist
        if __isSkip__(path, stream.url):
            Printf.success(aigpy.path.getFileName(path) + " (skip:already exists!)")
            return TidalTrackDownloadResult(True, path)

        urllib.request.urlretrieve(stream.url, path + '.part')
        print("Descarga completada con éxito.")

        # encrypted -> decrypt and remove encrypted file
        __encrypted__(stream, path + '.part', path)

        # contributors
        try:
            contributors = TIDAL_API.getTrackContributors(track.id)
        except:
            contributors = None

        # lyrics
        try:
            lyrics = TIDAL_API.getLyrics(track.id).subtitles
        except:
            lyrics = ''

        __setMetaData__(track, album, path, contributors, lyrics)
        Printf.success(track.title)
        return TidalTrackDownloadResult(True, path)
    except Exception as e:
        Printf.err(f"DL Track[{track.title}] failed.{str(e)}")
        result = TidalTrackDownloadResult(False, '')
        return result
