#!/bin/bash
MPD_IP=192.168.0.190

PID=$(ps aux | grep -v grep | grep -v start_pulseaudio.sh | grep pulseaudio | awk '{print $2}')
if [ ! -z "$PID" ]; then
  echo "Pulse is running, restarting ..."
  kill $PID
  sleep 3
fi
pulseaudio --load="module-native-protocol-tcp auth-ip-acl=${MPD_IP}" --exit-idle-time=900 --daemon