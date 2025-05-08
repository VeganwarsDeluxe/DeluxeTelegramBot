FROM python:3.12.2-alpine3.19
RUN apk add --no-cache git

WORKDIR /app

RUN apk add build-base libpq libpq-dev

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

RUN addgroup -g 2000 app && adduser -u 2000 -G app -s /bin/sh -D app && mkdir /app && chown 2000:2000 /app
USER 2000
WORKDIR /app

COPY . /app/

CMD [ "python3", "main.py" ]
