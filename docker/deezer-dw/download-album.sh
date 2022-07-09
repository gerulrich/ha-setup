#!/bin/bash
set -e
album=$1

if [ $UID -eq 0 ]; then
  echo "Run script as regular user"
  exit 1
fi

http_response=$(curl -s -o response.txt -w "%{http_code}" "https://api.deezer.com/album/$album")
if [ $http_response != "200" ]; then
  echo "No se pudo descargar info del album"
  exit 1
else
  data=$(cat response.txt)
  rm response.txt
  cover_url=$(echo $data | jq -r '.cover_xl')
  album_name=$(echo $data | jq -r '.title')
  upc=$(echo $data | jq -r '.upc')
  artist=$(echo $data | jq -r '.artist.name')
  dir=$(echo "$album_name - $artist [$upc]")
fi

echo "** Descargando $album_name - $artist **"

mkdir -p "$HOME/Songs/$dir"
wget -q -O "$HOME/Songs/$dir/cover.jpg" "$cover_url"
cp "$HOME/Songs/$dir/cover.jpg" "$HOME/Songs/$dir/folder.jpg"

deez-dw.py -so dee -l "https://www.deezer.com/en/album/$album" -q FLAC


album_discs=$(metaflac --show-tag=DISCNUMBER "$HOME/Songs/$dir/"*.flac | cut -d= -f2 | sort | uniq | wc -l)

OIFS="$IFS"
IFS=$'\n'
for file in $(ls "$HOME/Songs/$dir/"*.flac)
do
  echo "processing file: $file"
  if [ "$album_discs" -eq 1 ]; then
    metaflac --remove-tag=DISCNUMBER "$file"
  fi

  song_title="$(metaflac --show-tag=TITLE "$file" | cut -d= -f2)"
  track_number="$(metaflac --show-tag=TRACKNUMBER "$file" | cut -d= -f2)"
  disc_number="$(metaflac --show-tag=DISCNUMBER "$file" | cut -d= -f2)"

  # rename some special characters: /, :
  song_title="${song_title//\//;}"
  song_title="${song_title//:/ -}"

  new_file="$(printf "%02d" $track_number) $song_title.flac"
  if [ -z "$disc_number" ]; then
    mv "$file" "$HOME/Songs/$dir/$new_file"
  else
    mkdir -p "$HOME/Songs/$dir/CD${disc_number}"
    mv "$file" "$HOME/Songs/$dir/CD${disc_number}/$new_file"
  fi

done
IFS="$OIFS"

mkdir -p "$HOME/Songs/$artist"
mv "$HOME/Songs/$dir" "$HOME/Songs/$artist/$album_name"