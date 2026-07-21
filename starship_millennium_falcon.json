from sqlalchemy import func
from models import (Starship, Bid, ShipClass, 
                    SmugglerFaction, TransportMission, 
                    PlanetLocation, Character, RepublicCredit)

def get_average_bid_per_starship(session):
    print("\n--- 1. Average Bid per Starship ---")
    query = session.query(Starship.model_name, func.avg(Bid.amount)).join(Bid).group_by(Starship.id).all()
    for ship, avg_bid in query: 
        print(f"Schiff: {ship:<25} | Durchschnittliches Gebot: {avg_bid:,.2f} Credits")

def count_starships_per_class(session):
    print("\n--- 2. Starships per Class ---")
    # LÖSUNG: Wir joinen direkt über die Relationship "ShipClass.starships"
    query = session.query(ShipClass.class_name, func.count(Starship.id))\
        .join(ShipClass.starships).group_by(ShipClass.id).all()
    for s_class, count in query: 
        print(f"Klasse: {s_class:<25} | Anzahl Schiffe: {count}")

def get_transport_missions_per_faction(session):
    print("\n--- 3. Missions per Smuggler Faction ---")
    # LÖSUNG: Wir joinen direkt über die Relationship "SmugglerFaction.missions"
    query = session.query(SmugglerFaction.name, func.count(TransportMission.id))\
        .join(SmugglerFaction.missions).group_by(SmugglerFaction.id).all()
    for faction, count in query: 
        print(f"Fraktion: {faction:<23} | Missionen: {count}")

def get_highest_credit_balance_per_planet_sector(session):
    print("\n--- 4. Max Credit Balance per Sector ---")
    query = session.query(PlanetLocation.sector, func.max(RepublicCredit.account_balance))\
        .join(Character, PlanetLocation.character_id == Character.id)\
        .join(RepublicCredit, RepublicCredit.character_id == Character.id)\
        .group_by(PlanetLocation.sector).all()
    for sector, max_cred in query: 
        print(f"Sektor: {sector:<25} | Höchstes Guthaben: {max_cred:,.2f} Credits")

def count_bids_per_character(session):
    print("\n--- 5. Number of Bids per Character ---")
    query = session.query(Character.name, func.count(Bid.id)).join(Bid).group_by(Character.id).all()
    for char, count in query: 
        print(f"Charakter: {char:<22} | Anzahl abgegebener Gebote: {count}")

def run_all_queries(session):
    get_average_bid_per_starship(session)
    count_starships_per_class(session)
    get_transport_missions_per_faction(session)
    get_highest_credit_balance_per_planet_sector(session)
    count_bids_per_character(session)
    print("\n" + "="*60 + "\n")