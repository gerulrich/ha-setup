#!/bin/bash

#
# Generate an RSA ssh key pair with 4096 bits using the command
# $ ssh-keygen -t rsa -b 4096
#
# Copy public key in remote host 
# OpenWRT: System -> Administration -> SSH-Keys Tab.

ROUTER_IP="192.168.0.2"
KEY_FILE=~/id_rsa_tplink
TV_SHOWS_DIR=
GPG_KEY=
TELEGRAM_TOKEN=
TELEGRAM_URL="https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage"
CHAT_ID=
TV_SHOW_MEDIA_LOCATION=/media/seagate/series
ENCRYPTED_MEDIA_LOCATION=/media/seagate/.varios
OPEN_PORT_RULE_NAME='http odroid forward'