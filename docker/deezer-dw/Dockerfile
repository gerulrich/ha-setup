FROM python:3.9-slim
RUN useradd --create-home --shell /bin/bash user
WORKDIR /home/user
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    sed -i "s/need\['LYRICS_TEXT'\]/need['LYRICS_TEXT'] if 'LYRICS_TEXT' in need else ''/" \
      /usr/local/lib/python3.9/site-packages/deezloader/deezloader/__download__.py && \
    sed -i "s/need\['LYRICS_COPYRIGHTS'\]/need['LYRICS_COPYRIGHTS'] if 'LYRICS_COPYRIGHTS' in need else ''/" \
      /usr/local/lib/python3.9/site-packages/deezloader/deezloader/__download__.py && \
    sed -i "s/need\['LYRICS_WRITERS'\]/need['LYRICS_WRITERS'] if 'LYRICS_WRITERS' in need else ''/" \
      /usr/local/lib/python3.9/site-packages/deezloader/deezloader/__download__.py
USER user
COPY *.py /home/user
CMD [ "python3", "main.py" ]



