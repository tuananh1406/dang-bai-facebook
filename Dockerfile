FROM python:3.9

ENV DEBIAN_FRONTEND noninteractive
ENV FIREFOX_VER 87.0

RUN set -x \
   && apt update \
   && apt upgrade -y \
   && apt install -y \
       firefox-esr \
       pipenv \
       cron \
       iputils-ping

# Add latest FireFox
RUN set -x \
   && apt install -y \
       libx11-xcb1 \
       libdbus-glib-1-2 \
   && curl -sSLO https://download-installer.cdn.mozilla.net/pub/firefox/releases/${FIREFOX_VER}/linux-x86_64/en-US/firefox-${FIREFOX_VER}.tar.bz2 \
   && tar -jxf firefox-* \
   && mv firefox /opt/ \
   && chmod 755 /opt/firefox \
   && chmod 755 /opt/firefox/firefox

COPY . /app

RUN chmod 0644 /app/cron_conf && crontab /app/cron_conf

WORKDIR /app

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

CMD ['cron', '-f']
