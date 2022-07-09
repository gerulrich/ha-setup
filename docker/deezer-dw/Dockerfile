FROM python:3.9-slim
RUN useradd --create-home --shell /bin/bash user
RUN apt-get update && apt-get install -y bash flac jq curl wget
WORKDIR /home/user
RUN pip3 install deezloader
RUN mkdir -p /home/user/bin
RUN echo 'PATH=/home/user/bin:$PATH' >> /home/user/.bash_rc
COPY download-album.sh /home/user/bin
CMD [ "bash" ]
