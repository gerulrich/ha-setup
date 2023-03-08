import requests
from deezloader.deezloader import DeeLogin
import music_tag


def sanitize(value):
    invalid = '<>:"/\|?*&'
    for char in invalid:
        value = value.replace(char, '')
    return value


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
    return artist, album_name, tracks, upc, cover_url


# Get track info form deezer
def get_deezer_track_info(track):
    response = requests.get(f'https://api.deezer.com/track/{track}').json()
    contributors = []
    for c in response['contributors']:
        contributors.append(sanitize(c['name']))
    return response['track_position'], \
        sanitize(response['title']), \
        sanitize(response['title_short']), "  ".join(contributors), \
        response['disk_number'], response['isrc'], response['title_short'], response['title_version'] if 'title_version' in response else ''


# Download cover image from deezer
def download_deezer_cover(cover_url, destination_folder):
    img_response = requests.get(cover_url)
    if img_response.ok:
        with open(f'{destination_folder}/cover.jpg', 'wb') as f:
            f.write(img_response.content)


def download_deezer_track(track, quality, arl):
    downloader = DeeLogin(arl=arl)
    return downloader.download_trackdee(
        f'https://www.deezer.com/en/track/{track}',
        output_dir='./Songs',
        quality_download=quality,
        recursive_quality=False,
        recursive_download=False,
        not_interface=True,
        method_save=2
    )


def get_tracks_info(tracks):
    tracks_info = []
    multi_cd = False
    for track in tracks:
        nro, title, title_short, contributors, disk_number, isrc, song_title, title_version = get_deezer_track_info(track)
        tracks_info.append({
            'id': track,
            'track': nro,
            'title': title,
            'song_title': song_title,
            'title_short': title_short,
            'title_version': title_version,
            'contributors': contributors,
            'isrc': isrc,
            'disk_number': disk_number
        })
        if disk_number > 1:
            multi_cd = True
    return tracks_info, multi_cd




