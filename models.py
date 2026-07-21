# Star Wars Auktions- & Logistiksystem — Aufgabe 4 (Polyglot Persistence)

Erweiterung des relationalen Projekts aus Aufgabe 2 (SQLite + SQLAlchemy) um eine
**Graph-Datenbank (Neo4j)**, die das *soziale Schmuggler-Netzwerk* abbildet.

## Architektur (Polyglot Persistence)

| Speicher | Technologie | Inhalt |
|----------|-------------|--------|
| Relationale DB | SQLite (in-memory) + SQLAlchemy ORM | Schiffe, Auktionen, Gebote, Zahlungsmittel, Missionen, Fraktionen … |
| Graph-DB | Neo4j (Bolt) | Soziales Netzwerk: wer vertraut wem, wer schmuggelt mit wem, Rivalitäten, Fraktionszugehörigkeit |

**Brücke zwischen den DBs:** der `Character` aus der relationalen DB ist gleichzeitig
ein `(:Smuggler)`-Knoten im Graphen (`Smuggler.sql_id = Character.id`,
`Smuggler.name = Character.name`). Die Graph-Knoten werden direkt aus der
relationalen Session erzeugt — beide Speicher teilen sich also garantiert dieselben
Entitäten.

## Voraussetzungen

```bash
pip install -r requirements.txt
```

## Neo4j starten (Docker-Einzeiler)

```bash
docker run --name neo4j-sw -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password neo4j:5
```

- Neo4j Browser: <http://localhost:7474>  (Login: `neo4j` / `password`)
- Bolt-Endpunkt: `bolt://localhost:7687`

> Falls ein anderes Passwort verwendet wird, dieses in `main.py` (Variable
> `NEO4J_PASSWORD`) oder per Umgebungsvariable setzen:
>
> ```bash
> export NEO4J_URI=bolt://localhost:7687
> export NEO4J_USER=neo4j
> export NEO4J_PASSWORD=DEIN_PASSWORT
> ```

## Ausführen

```bash
python main.py
```

Ablauf von `main.py`:

1. Relationale DB im Speicher anlegen und mit Star-Wars-Daten befüllen (10 Charaktere).
2. Relationale Abfragen aus Aufgabe 1/2 ausführen.
3. Neo4j-Graph aus der relationalen Session + `input_files/social_network.json` aufbauen.
4. **3 Graph-Abfragen** ausführen (vertrauenswürdigste Schmuggler, kürzeste
   Vertrauenskette, Partner-Empfehlung).
5. **2 Polyglot-Abfragen** ausführen (Auktions-Vertrauenscheck, sichere Crew-Empfehlung).

Ist Neo4j nicht erreichbar, läuft der relationale Teil trotzdem durch; der Graph-Teil
wird mit einem Hinweis übersprungen.

## Projektstruktur

```
StarWarsProject/
├── models.py            # SQLAlchemy ORM-Modelle (relationale DB)
├── queries.py           # Relationale Abfragen (Aufgabe 1/2)
├── file_io.py           # JSON-Import der dateibasierten Entities (Aufgabe 2)
├── graph_db.py          # NEU: Neo4j-Schicht (Aufbau + 3 Graph-Abfragen)
├── polyglot.py          # NEU: 2 Polyglot-Abfragen über beide DBs
├── main.py              # Orchestrierung relational + Graph + Polyglot
├── requirements.txt
├── input_files/
│   ├── social_network.json   # NEU: Vertrauens-/Schmuggel-/Rivalitäts-Kanten
│   └── …                     # Aufgabe-2-Importdateien
└── output_files/             # Aufgabe-2-Ergebnisdateien
```

## Neo4j-Version

Getestet gegen Neo4j 5.x (Bolt). Die Constraint-Erzeugung ist versionssicher
gekapselt, sodass auch ältere 4.x-Instanzen ohne Fehler durchlaufen.
