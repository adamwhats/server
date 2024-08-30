FROM alpine:3.18

RUN apk update && apk add --no-cache bash python3 py3-pip git

RUN pip install requests docker

RUN git clone https://github.com/343max/eero-client.git /opt/eero-client \
    && pip install /opt/eero-client

COPY ./cron_jobs/crontab /etc/crontabs/root
COPY ./cron_jobs/jobs/ /usr/local/bin/

CMD ["crond", "-f", "-l", "2"]