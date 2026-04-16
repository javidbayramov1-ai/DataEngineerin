from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importiere Base und alle Klassen aus models.py
from models import (Base, Character, PlanetLocation, Starship, ShipClass, HoloRecord, 
                    Bid, RepublicCredit, SpiceBarter, Spaceport, DockingBay, 
                    SmugglerFaction, TransportMission)

# Importiere die Query-Funktionen
from queries import run_all_queries

def populate_db(session):
    print("Befülle die Datenbank mit Star Wars Mock-Daten...")
    
    # 1. Characters
    han = Character(name="Han Solo")
    luke = Character(name="Luke Skywalker")
    lando = Character(name="Lando Calrissian")
    boba = Character(name="Boba Fett")
    
    # 2. Locations
    tatooine = PlanetLocation(planet_name="Tatooine", sector="Outer Rim", character=luke)
    coruscant = PlanetLocation(planet_name="Coruscant", sector="Core Worlds", character=han)
    bespin = PlanetLocation(planet_name="Bespin", sector="Outer Rim", character=lando)
    
    # 3. Payment Methods
    han_credits = RepublicCredit(account_balance=50000.0, character=han)
    lando_credits = RepublicCredit(account_balance=950000.0, character=lando)
    luke_spice = SpiceBarter(spice_type="Kessel", kilos=5.5, character=luke)
    boba_credits = RepublicCredit(account_balance=150000.0, character=boba)
    
    # 4. Categories / Ship Classes
    freighter = ShipClass(class_name="Light Freighter")
    fighter = ShipClass(class_name="Starfighter")
    interceptor = ShipClass(class_name="Interceptor")
    
    # 5. Starships
    falcon = Starship(model_name="Millennium Falcon", seller=han, ship_classes=[freighter])
    xwing = Starship(model_name="X-Wing T-65", seller=luke, ship_classes=[fighter])
    slave1 = Starship(model_name="Firespray-31 (Slave I)", seller=boba, ship_classes=[freighter, interceptor])
    
    # 6. Holo Records (Bilder/Videos für die Inserate)
    holo1 = HoloRecord(file_path="/holonet/falcon_front.holo", resolution="1080p", starship=falcon)
    holo2 = HoloRecord(file_path="/holonet/xwing_engine.holo", resolution="720p", starship=xwing)
    
    # 7. Bids (Gebote)
    bid1 = Bid(amount=100000, bidder=luke, starship=falcon)
    bid2 = Bid(amount=120000, bidder=lando, starship=falcon)
    bid3 = Bid(amount=50000, bidder=han, starship=xwing)
    bid4 = Bid(amount=200000, bidder=lando, starship=slave1)
    bid5 = Bid(amount=215000, bidder=han, starship=slave1)
    
    # 8. Spaceports, Bays & Factions
    mos_eisley = Spaceport(name="Mos Eisley Spaceport")
    cloud_city_port = Spaceport(name="Cloud City Platform")
    
    bay94 = DockingBay(bay_number="94", spaceport=mos_eisley)
    bay327 = DockingBay(bay_number="327", spaceport=cloud_city_port)
    
    hutt_cartel = SmugglerFaction(name="Hutt Cartel")
    pyke_syndicate = SmugglerFaction(name="Pyke Syndicate")
    
    # 9. Transport Missions
    mission1 = TransportMission(tracking_code="Kessel-Run-12", destination=tatooine, origin_spaceport=mos_eisley, factions=[hutt_cartel])
    mission2 = TransportMission(tracking_code="Bespin-Drop-01", destination=bespin, origin_spaceport=cloud_city_port, factions=[hutt_cartel, pyke_syndicate])
    mission3 = TransportMission(tracking_code="Coruscant-Express", destination=coruscant, origin_spaceport=mos_eisley, factions=[pyke_syndicate])
    
    # Alles zur Session hinzufügen und committen
    session.add_all([han, luke, lando, boba, tatooine, coruscant, bespin, 
                     han_credits, lando_credits, luke_spice, boba_credits,
                     freighter, fighter, interceptor, falcon, xwing, slave1,
                     holo1, holo2, bid1, bid2, bid3, bid4, bid5,
                     mos_eisley, cloud_city_port, bay94, bay327, 
                     hutt_cartel, pyke_syndicate, mission1, mission2, mission3])
    
    session.commit()
    print("Datenbank erfolgreich befüllt!\n")

if __name__ == "__main__":
    # In-Memory SQLite DB (Wird bei jedem Start neu erstellt)
    engine = create_engine('sqlite:///:memory:', echo=False) 
    # Hinweis: Setze echo=True, wenn du die im Hintergrund generierten SQL-Befehle sehen willst
    
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # 1. Daten generieren
    populate_db(session)
    
    # 2. Queries ausführen
    run_all_queries(session)