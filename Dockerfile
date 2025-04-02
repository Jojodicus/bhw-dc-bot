FROM python:3.11-alpine

RUN apk add --no-cache git

WORKDIR /bhw-bot

COPY . ./

RUN pip install -r requirements.txt

ENTRYPOINT [ "python3", "main.py" ]
