FROM python:3.11

#ENV BOT_NAME=$BOT_NAME
#ENV BOT_TOKEN=$BOT_TOKEN
#ENV DB_DATABASE=$DB_DATABASE
#ENV DB_USER=$DB_USER
#ENV DB_PASSWORD=$DB_PASSWORD
#ENV DB_HOST=$DB_HOST
#ENV DB_PORT=$DB_PORT
#ENV MESSAGE_LIVE=$MESSAGE_LIVE
#ENV ADMIN_FIRST=$ADMIN_FIRST
#ENV ADMIN_SECOND=$ADMIN_SECOND
#ENV LOG_FILE=$LOG_FILE
#ENV TZ=$TZ

WORKDIR /usr/src/app/"${kidney_scanner}"
COPY requirements.txt /usr/src/app/"${kidney_scanner}"
RUN pip install -r /usr/src/app/"${kidney_scanner}"/requirements.txt
COPY . /usr/src/app/"${kidney_scanner}"
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

CMD python3 -m app --config ./config/config.yaml
