#!/bin/bash
set -e
if [ ! -f "$HOME"/flow/channels.json ]; then
  python3 flow-api.py --channels
  if [ -f "$HOME/flow/post_channel_update.sh" ]; then
    echo "Executing post_channel_update.sh"
    bash "$HOME"/flow/post_channel_update.sh
  else
    echo "Script post_channel_update.sh not found"
  fi
fi
python3 flow-api.py --epg
if [ -f "$HOME"/flow/post_epg_update.sh ]; then
  echo "Executing post_epg_update.sh"
  bash "$HOME"/flow/post_epg_update.sh
else
  echo "script post_epg_update.sh not found"
fi