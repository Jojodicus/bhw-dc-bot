# Bens Hardware Discord Bot

Helferlein für die Bens Hardware Discord Community

## Features

- Erkennt Pings an Bens_Hardware#0438 und weist den Nutzer auf die entsprechenden Regeln hin
- Findet Links zu lokalen und/oder nicht-öffentlichen [Geizhals](https://geizhals.de/) Listen in Nachrichten und erklärt, wie man diese öffentlich macht
- diverse [%](#-commands) Commands für Hardware-Empfehlungen von Ben und generell QOL für Hardware-Support
- [/](#-commands-1) Commands für Administration und Konfiguation des Bots

## Installation und Ausführung

Zum Hosten des Bots wird ein Linux System mit Python3.10 empfohlen.

```bash
git clone https://github.com/Jojodicus/bhw-dc-bot
cd bhw-dc-bot
pip install -r requirements.txt
mkdir .cache
nano .env # BHW_TOKEN und GH_API_COOKIE entsprechend setzen
# Datei ausführbar machen, ansonsten via `python3 main.py` starten
chmod +x main.py
```

Danach kann der Bot mittels `./main.py` ausgeführt werden. Um das ganze auf zB einem v-server persistent zu halten ist das Tool `tmux` zu empfehlen. Nutzung dazu:

```bash
tmux
# tmux env öffnet sich
./main.py # start wie normal
# um env in den Hintergrund zu schieben: 'Strg'+'b', dann 'd'
... # hier auch logout möglich
# zum in den Vordergrund holen:
tmux attach
```

## %-Commands

Commands werden mit % geprefixt. Zur Ausführung benötigt man mindestens die Rolle `Silber` (sofern diese auf dem Server existiert).

Unterstützte Befehle:

| Command | Beschreibung |
|---------|--------------|
| %help   | Zeig eine Hilfe an, verlinkt hierher |
| %1tbssd | Bens Empfehlungen für 1TB-SSDs |
| %2tbssd | Bens Empfehlungen für 2TB-SSDs |
| %4tbssd | Bens Empfehlungen für 4TB-SSDs |
| %aio    | Bens Empfehlungen für AiO-Wasserkühlungen |
| %case   | Bens Empfehlungen für Gehäuse |
| %cpukühler | Bens Empfehlungen für Luftkühler |
| %lüfter | Bens Empfehlungen für non-RGB-Lüfter |
| %netzteil | Bens Empfehlungen für Netzteile |
| %ram    | Bens Empfehlungen für Arbeitsspeicher |
| %rgblüfter | Bens Empfehlungen für RGB-Lüfter |
| %meta | Weist einen Nutzer auf eine Metafrage hin |
| %gpu-ranking (resolution) | Sendet eine Benchmark-Grafik zum Vergleich aktueller Grafikkarten in FHD/WQHD/UHD auf Basis von [tom'sHARDWARE](https://www.tomshardware.com/reviews/gpu-hierarchy,4388.html). |
| %psu | Sendet eine Übersicht von Tier-A Netzteilen auf Basis von [CULTISTS NETWORK](https://cultists.network/140/psu-tier-list/) nach Leistung sortiert |


## /-Commands

Die Konfiguration des Bots wird mittels Slash-Commands realisiert. Diese sind auf Serveradministratoren beschränkt. Der Vorteil von Slash-Commands ist, dass diese mitsamt Beschreibung in der Command-Übersicht auftauchen und man somit schnell die richtige Syntax findet.

Unterstützte Befehle:

| Command | Beschreibung |
|---------|--------------|
| /ping   | Überprüft Online-Status sowie Latenz des Bots |
| /reload | Startet den Bot neu |
| /update | Holt sich via `git pull` den aktuellsten Quellcode und startet danach neu |
