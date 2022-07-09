FROM python:3.9-alpine3.15
#RUN useradd --create-home --shell /bin/bash app_user
RUN apt-get update && apt-get install -y mosquitto-clients jq
#WORKDIR /home/app_user
COPY requirements.txt ./
#USER app_user
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["bash"]