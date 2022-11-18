#!/bin/bash

DIR=$(dirname $0)
. $DIR/env.sh

# Regular expressions
TV_SHOW_FILE_REGEX='.*\(S[0-9][0-9]E[0-9][0-9]\).*'
SHOW_NAME_REGEX='s/\(.*\)\.S[0-9][0-9].*/\1/'
SHOW_SEASON_REGEX='s/.*S\([0-9][0-9]\).*/\1/'
SHOW_EPISODE_REGEX='s/.*\(s[0-9][0-9]e[0-9][0-9]\).*/\1/'
AWK_CAPITALIZE='{for (i=1; i<=NF; ++i) { $i=toupper(substr($i,1,1)) tolower(substr($i,2)); } print }'

# Get torrent id and files
tr_name=$(echo "$1" | sed -e 's/\[[^][]*\]//g')
id=$(transmission-remote -l | grep "$tr_name" | tr -s "[:blank:]" | cut -d' ' -f2 | sed 's/\*//')
files=$(transmission-remote -t $id -f | tr -s ' ' | cut -d' ' -f8)
location=$(transmission-remote -t $id -i | grep Location | cut -d' ' -f4)


if [ "$location" == "${ENCRYPTED_MEDIA_LOCATION}" ]; then
    /usr/bin/curl --insecure -X POST $TELEGRAM_URL -d chat_id=$CHAT_ID -d text="Download completed"
    for file in $files; do
        filename=$(basename $file)
        extension="${filename##*.}"
        dir=$(dirname $file)
        if [ "$extension" = "mp4" ] || [ $extension = "mkv" ];
        then
            gpg --output "/media/seagate/.varios/${filename}.gpg" --encrypt -r ${GPG_KEY} "$location/$file" && \
            /usr/bin/curl --insecure -X POST $TELEGRAM_URL -d chat_id=$CHAT_ID -d text="Done." &
        fi
    done
    transmission-remote --torrent "$id" --delete
    sleep 480 && rm -rf "$dir" &
    exit 0
fi


if [ ! -z ${TELEGRAM_TOKEN} ]; then
    /usr/bin/curl -X POST $TELEGRAM_URL -d chat_id=$CHAT_ID -d text="Download completed: $1"
else
    echo "Telegram token is not set"
fi

if [ "$location" == "${TV_SHOW_MEDIA_LOCATION}"  ]; then
    for file in $files; do
        upper=$(echo $file | awk '{ print toupper($0) }')
        match=$(expr match "$upper" ${TV_SHOW_FILE_REGEX})
        if [ ! -z $match ]; then
            filename=$(basename $file)
            extension="${filename##*.}"
            if [ "$extension" = "mp4" ] || [ $extension = "mkv" ]; then
                show=$(echo $filename | awk '{ print toupper($0) }' | sed ${SHOW_NAME_REGEX} | sed 's/\./ /g' | awk ${AWK_CAPITALIZE})
                season=$(echo $filename | awk '{ print toupper($0) }' |  sed ${SHOW_SEASON_REGEX} | sed 's/^[0]\(.*\)/\1/')
                episode=$(echo $filename | awk '{print tolower($0)}' | sed ${SHOW_EPISODE_REGEX})
                echo "Show name ${show}, episode ${episode}"
                mkdir -p "$TV_SHOWS_DIR/$show/Season $season"
                dest="$TV_SHOWS_DIR/$show/Season $season/$show"_$episode.$extension
                if [ ! -f "$dest" ]; then
                    echo "file $dest not exists, creating link"
                    ln "$location/$file" "$dest"
                fi
            fi
        fi
    done
fi