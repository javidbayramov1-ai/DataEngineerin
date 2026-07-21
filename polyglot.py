"""
graph_db.py  -  Polyglot Persistence: Graph-Datenbank-Schicht (Neo4j)
=====================================================================
Diese Schicht ergaenzt die relationale DB (SQLite/SQLAlchemy) aus Aufgabe 2
um eine Graph-Datenbank. Im Graph wird das *soziale* Schmuggler-Netzwerk
abgebildet - also Beziehungen, die in einer relationalen DB nur muehsam
(viele Self-Joins, rekursive CTEs) abfragbar waeren.

Knotentypen:
    (:Smuggler {sql_id, name})   gespiegelt aus Character (sql_id = Character.id)
    (:Faction  {name})           gespiegelt aus SmugglerFaction

Beziehungstypen:
    (:Smuggler)-[:TRUSTS {level}]->(:Smuggler)
    (:Smuggler)-[:SMUGGLED_WITH {missions}]-(:Smuggler)
    (:Smuggler)-[:RIVAL_OF]-(:Smuggler)
    (:Smuggler)-[:MEMBER_OF]->(:Faction)

Voraussetzung: laufende Neo4j-Instanz (siehe README.md, Docker-Einzeiler).
"""

import json
import os
from neo4j import GraphDatabase

from models import Character, SmugglerFaction


class SmugglerGraph:
    """Kapselt die Verbindung zur Neo4j-Datenbank und alle Graph-Operationen."""

    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    # ---------------------------------------------------------------
    # STORE  -  Daten in der Graph-DB speichern
    # ---------------------------------------------------------------
    def clear(self):
        """Loescht den kompletten Graphen (fuer saubere Wiederholungslaeufe)."""
        with self._driver.session() as s:
            s.run("MATCH (n) DETACH DELETE n")

    def build_from_relational(self, session, social_file):
        """
        Baut den Graphen auf. Knoten kommen aus der RELATIONALEN DB
        (so ist garantiert, dass beide Speicher dieselben Entitaeten teilen),
        die Beziehungen kommen aus social_network.json.
        """
        # 1) Knoten aus der relationalen DB spiegeln (die "Bruecke")
        characters = session.query(Character).all()
        factions = session.query(SmugglerFaction).all()

        # Eindeutigkeit absichern (Syntax variiert je Neo4j-Version -> nicht fatal)
        with self._driver.session() as s:
            for c in ("FOR (x:Smuggler) REQUIRE x.name IS UNIQUE",
                      "FOR (f:Faction) REQUIRE f.name IS UNIQUE"):
                try:
                    s.run(f"CREATE CONSTRAINT IF NOT EXISTS {c}")
                except Exception:
                    pass  # aeltere Neo4j-Version: ohne Constraint weiterarbeiten

        with self._driver.session() as s:
            for c in characters:
                s.run("MERGE (x:Smuggler {name: $name}) SET x.sql_id = $sql_id",
                      name=c.name, sql_id=c.id)
            for f in factions:
                s.run("MERGE (f:Faction {name: $name})", name=f.name)

        # 2) Soziale Beziehungen aus JSON laden (mirror des Ex2-Datei-Patterns)
        with open(social_file, "r", encoding="utf-8") as fh:
            social = json.load(fh)

        with self._driver.session() as s:
            for t in social["trusts"]:
                s.run(
                    "MATCH (a:Smuggler {name:$a}), (b:Smuggler {name:$b}) "
                    "MERGE (a)-[r:TRUSTS]->(b) SET r.level = $lvl",
                    a=t["from"], b=t["to"], lvl=t["level"])

            for e in social["smuggled_with"]:
                s.run(
                    "MATCH (a:Smuggler {name:$a}), (b:Smuggler {name:$b}) "
                    "MERGE (a)-[r:SMUGGLED_WITH]->(b) SET r.missions = $m",
                    a=e["a"], b=e["b"], m=e["missions"])

            for e in social["rivals"]:
                s.run(
                    "MATCH (a:Smuggler {name:$a}), (b:Smuggler {name:$b}) "
                    "MERGE (a)-[:RIVAL_OF]->(b)",
                    a=e["a"], b=e["b"])

            for m in social["memberships"]:
                s.run(
                    "MATCH (a:Smuggler {name:$a}), (f:Faction {name:$f}) "
                    "MERGE (a)-[:MEMBER_OF]->(f)",
                    a=m["smuggler"], f=m["faction"])

        print("Graph erfolgreich aufgebaut "
              f"({len(characters)} Smuggler, {len(factions)} Fraktionen).")

    # ---------------------------------------------------------------
    # QUERY 1  -  Wer ist der vertrauenswuerdigste Schmuggler?
    # (gewichteter Eingangsgrad ueber TRUSTS - Degree Centrality)
    # ---------------------------------------------------------------
    def most_trusted_smugglers(self, limit=5):
        cypher = """
        MATCH (s:Smuggler)<-[t:TRUSTS]-(:Smuggler)
        RETURN s.name              AS smuggler,
               count(t)            AS trusted_by,
               sum(t.level)        AS trust_score
        ORDER BY trust_score DESC, trusted_by DESC
        LIMIT $limit
        """
        with self._driver.session() as s:
            return [r.data() for r in s.run(cypher, limit=limit)]

    # ---------------------------------------------------------------
    # QUERY 2  -  Kuerzeste Vertrauenskette zwischen zwei Schmugglern
    # ("Wie komme ich ueber Vertrauensleute an X heran?")
    # ---------------------------------------------------------------
    def trust_path(self, from_name, to_name, max_hops=6):
        cypher = f"""
        MATCH (a:Smuggler {{name:$a}}), (b:Smuggler {{name:$b}}),
              p = shortestPath((a)-[:TRUSTS*..{max_hops}]->(b))
        RETURN [n IN nodes(p) | n.name] AS chain,
               length(p)                AS hops
        """
        with self._driver.session() as s:
            rec = s.run(cypher, a=from_name, b=to_name).single()
            return rec.data() if rec else None

    # ---------------------------------------------------------------
    # QUERY 3  -  Partner-Empfehlung (Friends-of-Friends im Trust-Netz)
    # Empfehle Schmuggler, die von Vertrauensleuten vertraut werden,
    # die der Nutzer aber noch nicht kennt und mit denen er noch nie
    # geschmuggelt hat.
    # ---------------------------------------------------------------
    def recommend_partners(self, name):
        cypher = """
        MATCH (me:Smuggler {name:$name})-[:TRUSTS]->(mid:Smuggler)-[:TRUSTS]->(cand:Smuggler)
        WHERE cand <> me
          AND NOT (me)-[:TRUSTS]->(cand)
          AND NOT (me)-[:SMUGGLED_WITH]-(cand)
        RETURN cand.name                 AS recommended,
               count(DISTINCT mid)       AS mutual_contacts,
               collect(DISTINCT mid.name) AS via
        ORDER BY mutual_contacts DESC, recommended
        """
        with self._driver.session() as s:
            return [r.data() for r in s.run(cypher, name=name)]

    # ---------------------------------------------------------------
    # HELPER fuer Polyglot-Abfragen
    # ---------------------------------------------------------------
    def trusted_by(self, name):
        """Gibt {name: level} aller direkt vertrauten Schmuggler zurueck."""
        cypher = ("MATCH (s:Smuggler {name:$name})-[t:TRUSTS]->(b:Smuggler) "
                  "RETURN b.name AS name, t.level AS level")
        with self._driver.session() as s:
            return {r["name"]: r["level"] for r in s.run(cypher, name=name)}

    def faction_trusted_crew(self, faction_name):
        """
        Mitglieder einer Fraktion, die mit mindestens einem anderen Mitglied
        DERSELBEN Fraktion in *gegenseitigem* Vertrauen stehen (sichere Crew).
        Liefert [{member, partners:[...]}].
        """
        cypher = """
        MATCH (f:Faction {name:$f})<-[:MEMBER_OF]-(a:Smuggler)
        MATCH (a)-[:TRUSTS]->(b:Smuggler)-[:TRUSTS]->(a)
        WHERE (b)-[:MEMBER_OF]->(f)
        RETURN a.name AS member, collect(DISTINCT b.name) AS partners
        ORDER BY size(partners) DESC, member
        """
        with self._driver.session() as s:
            return [r.data() for r in s.run(cypher, f=faction_name)]
