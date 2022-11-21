FROM python:3.9-slim
RUN useradd --create-home --shell /bin/bash user
WORKDIR /home/user
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
USER user
COPY main.py /home/user
CMD [ "python3", "main.py" ]