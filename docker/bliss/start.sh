#!/bin/bash

docker run -d --name=bliss \
  -v /storage/music:/music \
  -v /storage/docker/bliss/config:/config \
  -e PGID=0 -e PUID=0 \
  -e TZ=America/Argentina/Buenos_Aires \
  -p 3220:3220 \
  -p 3221:3221 \
  gerulrich/bliss