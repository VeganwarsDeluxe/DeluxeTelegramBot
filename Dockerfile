FROM python:3.12.2-alpine3.19
RUN apk add --no-cache git build-base libpq libpq-dev

RUN addgroup -g 2000 app && adduser -u 2000 -G app -s /bin/sh -D app && mkdir /app && chown 2000:2000 /app
USER 2000
WORKDIR /app

COPY . .
RUN python3 -m venv venv 
RUN python3 /app/venv/bin/pip install --no-cache-dir -r requirements.txt
RUN rm -rf .cache/pip

ENTRYPOINT [ "/app/venv/bin/python", "main.py" ]

