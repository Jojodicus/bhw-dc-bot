# Bens Hardware Discord Bot

Helferlein für die Bens Hardware Discord Community

## Features

- Erkennt Pings an Bens_Hardware#0438 und weist den Nutzer auf die entsprechenden Regeln hin
- Findet Links zu lokalen und/oder nicht-öffentlichen [Geizhals](https://geizhals.de/) Listen in Nachrichten und erklärt, wie man diese öffentlich macht
- diverse [%](#-commands) Commands für Hardware-Empfehlungen von Ben und generell QOL für Hardware-Support
- [/](#-commands-1) Commands für Administration und Konfiguation des Bots

## Installation und Ausführung

Zum Hosten des Bots wird ein Linux System mit Docker empfohlen.
Die `.env` Datei sollte in etwa so aussehen:

```bash
BHW_TOKEN='xxx'
GH_API_COOKIE='csrf=xxx'
SERPAPI_KEY='xxx'
```

Danach kann der Bot mittels Docker ausgeführt werden:

```bash
git clone https://github.com/Jojodicus/bhw-dc-bot
cd bhw-dc-bot
sudo docker build -t bhw-dc-bot .
sudo docker run -d bhw-dc-bot
```

Wahlweise natürlich auch in einem Compose-Stack.

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
| %dd4    | Bens Empfehlungen für DDR4 Arbeitsspeicher |
| %dd5    | Bens Empfehlungen für DDR5 Arbeitsspeicher |
| %rgblüfter | Bens Empfehlungen für RGB-Lüfter |
| %meta | Weist einen Nutzer auf eine Metafrage hin |
| %gpu-ranking (resolution) | Sendet eine Benchmark-Grafik zum Vergleich aktueller Grafikkarten in FHD/WQHD/UHD auf Basis von [tom'sHARDWARE](https://www.tomshardware.com/reviews/gpu-hierarchy,4388.html). |
| %cpu-ranking \[typ\] | Sendet eine Benchmark-Grafik zum Vergleich aktueller Prozessoren auf Basis von [tom'sHARDWARE](https://www.tomshardware.com/reviews/cpu-hierarchy,4312.html). |
| %psu (wattage) | Sendet eine Übersicht von Netzteilen auf Basis von [CULTISTS NETWORK](https://cultists.network/140/psu-tier-list/) nach Leistung/Preis sortiert |
<!--(broken) | %gidf (query) | Google ist dein Freund, sucht einen Begriff auf Google und zeigt ein paar der ersten passenden Ergebnisse an | -->


## /-Commands

Die Konfiguration des Bots wird mittels Slash-Commands realisiert. Diese sind auf Serveradministratoren beschränkt. Der Vorteil von Slash-Commands ist, dass diese mitsamt Beschreibung in der Command-Übersicht auftauchen und man somit schnell die richtige Syntax findet.

Unterstützte Befehle:

| Command | Beschreibung |
|---------|--------------|
| /ping   | Überprüft Online-Status sowie Latenz des Bots |
| /reload | Startet den Bot neu |
| /update | Holt sich via `git pull` den aktuellsten Quellcode und startet danach neu |
