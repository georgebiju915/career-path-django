# core/neo4j_client.py
from neo4j import GraphDatabase
from django.conf import settings

_driver = None

def get_driver():
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD))
    return _driver

def create_skill(name, aliases=None):
    with get_driver().session() as session:
        session.run("""
            MERGE (s:Skill {name:$name})
            ON CREATE SET s.aliases = $aliases, s.created_at = datetime()
        """, name=name, aliases=aliases or [])
