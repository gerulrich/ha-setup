## How to run

- Create deez_settings.ini file with this content:
```
[deez_login]
mail=<email>
pwd=<password>
arl=<arl session cookie>

[spot_login]
mail=
pwd=
```

Docker comand:
```
docker run -it -p 8001:8000 -v $PWD/downloads/:/home/user/Songs -v $PWD/deez_settings.ini:/home/user/.deez_settings.ini --rm gerulrich/deezer-dw
$ su - user # inside container
$ download-album.sh <deezer album id>
```

# Download with freyrjs
```
docker run -it --rm -v $PWD:/data freyrcli/freyrjs <URL spotify|apple music|dezeer>
```

