FROM ghcr.io/astral-sh/uv:debian-slim

WORKDIR /bhw-dc-bot

ENV PYTHONUNBUFFERED=1

RUN apt-get -y update && apt-get -y install tesseract-ocr

COPY . .

RUN uv sync --compile-bytecode

ENTRYPOINT [ "uv", "run", "bot/main.py" ]
