FROM python:3.12.2-alpine3.19
RUN apk add --no-cache git build-base libpq libpq-dev

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /app

RUN addgroup -g 2000 app && adduser -u 2000 -G app -s /bin/sh -D app && chown -R 2000:2000 /app
USER 2000

ENTRYPOINT [ "python3", "main.py" ]

