# Bens Hardware Discord Bot

Helferlein für die Bens Hardware Discord Community

## Features

- Erkennt Pings an `bens_hardware` und weist den Nutzer auf die entsprechenden Regeln hin
- Findet Links zu lokalen und/oder nicht-öffentlichen [Geizhals](https://geizhals.de/) Listen in Nachrichten und erklärt, wie man diese öffentlich macht
- Erkennt fTPM-Reset Bildschirmaufnahmen und erklärt, wie man dort mit deutscher Tastatur weiter kommt
- Erkennt Metafragen und erklärt, wie man richtig Fragen stellt

### Befehle

- `%help` - Zeit eine kurze Hilfe mit Link zu diesem Repo
- `%meta` - Antwortet auf die referenzierte Nachricht mit dem Text zu Metafragen
- `%tpm` - Antwortet auf die referenzierte Nachricht mit dem Text zum fTPM-Reset
- `%gpu <res1> (<res2>)...` - Schickt ein Bild vom aktuellen TomsHardware GPU Benchmark zu den angegebenen Auflösungen
- `%ai <message>` - Frag die AI nach einer Antwort

## Verwendung

### Lokal

- `uv` installieren
- Für TPM-Erkennung: [`tesseract`](https://tesseract-ocr.github.io/) installieren

```sh
uv run --env-file .env bot/main.py
```

### Docker

Direkt:
```sh
docker run --rm -ite BHW_TOKEN=[dein token] $(docker build -q .)
```

Compose:
```yaml
services:
  bhw-bot:
    container_name: bhw-bot
    build: . # Pfad zu diesem Repo
    restart: unless-stopped
    environment:
      BHW_TOKEN: dein token
```

### Ruff

Als Linter und Formatter wird Ruff benutzt:

```sh
uvx ruff check --select I --fix # imports
uvx ruff format
```
