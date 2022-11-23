# build docker image

```
docker build -t deezer-dw .
```

# run docker container

```
docker run -e MQTT_HOST=<host> -e MQTT_USER=<user> -e MQTT_PASS=<pass> \
    -e ARL_COOKIE=<arl> \
    -v $path/Downloads:/home/user/Songs \
    --name deezer deezer-dw
```