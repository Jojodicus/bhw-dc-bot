FROM ghcr.io/astral-sh/uv:alpine

WORKDIR /bhw-dc-bot
COPY * .

RUN uv sync --compile-bytecode

ENTRYPOINT [ "uv", "run", "main.py" ]
