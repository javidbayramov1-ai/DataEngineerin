from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# --- ASSOCIATION TABLES (Many-to-Many) ---
starship_class_table = Table('starship_class', Base.metadata,
    Column('starship_id', Integer, ForeignKey('starships.id')),
    Column('shipclass_id', Integer, ForeignKey('shipclasses.id'))
)

mission_faction_table = Table('mission_faction', Base.metadata,
    Column('mission_id', Integer, ForeignKey('transport_missions.id')),
    Column('faction_id', Integer, ForeignKey('smuggler_factions.id'))
)

# --- ENTITIES ---
class Character(Base):
    __tablename__ = 'characters'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    locations = relationship("PlanetLocation", back_populates="character")
    bids = relationship("Bid", back_populates="bidder")
    payment_methods = relationship("PaymentMethod", back_populates="character")
    starships_for_sale = relationship("Starship", back_populates="seller")

    def __repr__(self):
        return f"<Character(name='{self.name}')>"

class PlanetLocation(Base):
    __tablename__ = 'planet_locations'
    id = Column(Integer, primary_key=True)
    planet_name = Column(String)
    sector = Column(String)
    character_id = Column(Integer, ForeignKey('characters.id'))
    
    character = relationship("Character", back_populates="locations")

class Starship(Base):
    __tablename__ = 'starships'
    id = Column(Integer, primary_key=True)
    model_name = Column(String)
    seller_id = Column(Integer, ForeignKey('characters.id'))
    
    seller = relationship("Character", back_populates="starships_for_sale")
    bids = relationship("Bid", back_populates="starship")
    holo_records = relationship("HoloRecord", back_populates="starship")
    ship_classes = relationship("ShipClass", secondary=starship_class_table, back_populates="starships")

    def __repr__(self):
        return f"<Starship(model='{self.model_name}')>"

class ShipClass(Base):
    __tablename__ = 'shipclasses'
    id = Column(Integer, primary_key=True)
    class_name = Column(String)
    
    starships = relationship("Starship", secondary=starship_class_table, back_populates="ship_classes")

class HoloRecord(Base):
    __tablename__ = 'holo_records'
    id = Column(Integer, primary_key=True)
    file_path = Column(String)
    resolution = Column(String)
    starship_id = Column(Integer, ForeignKey('starships.id'))
    
    starship = relationship("Starship", back_populates="holo_records")

class Bid(Base):
    __tablename__ = 'bids'
    id = Column(Integer, primary_key=True)
    amount = Column(Float)
    bidder_id = Column(Integer, ForeignKey('characters.id'))
    starship_id = Column(Integer, ForeignKey('starships.id'))
    
    bidder = relationship("Character", back_populates="bids")
    starship = relationship("Starship", back_populates="bids")

# --- INHERITANCE: Payment Methods ---
class PaymentMethod(Base):
    __tablename__ = 'payment_methods'
    id = Column(Integer, primary_key=True)
    type = Column(String)
    character_id = Column(Integer, ForeignKey('characters.id'))
    
    character = relationship("Character", back_populates="payment_methods")
    
    __mapper_args__ = {
        'polymorphic_identity': 'payment_method',
        'polymorphic_on': type
    }

class RepublicCredit(PaymentMethod):
    __tablename__ = 'republic_credits'
    id = Column(Integer, ForeignKey('payment_methods.id'), primary_key=True)
    account_balance = Column(Float)
    
    __mapper_args__ = {'polymorphic_identity': 'republic_credit'}

class SpiceBarter(PaymentMethod):
    __tablename__ = 'spice_barters'
    id = Column(Integer, ForeignKey('payment_methods.id'), primary_key=True)
    spice_type = Column(String)
    kilos = Column(Float)
    
    __mapper_args__ = {'polymorphic_identity': 'spice_barter'}

# --- TRANSPORT & LOGISTICS ---
class Spaceport(Base):
    __tablename__ = 'spaceports'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    docking_bays = relationship("DockingBay", back_populates="spaceport")
    missions = relationship("TransportMission", back_populates="origin_spaceport")

class DockingBay(Base):
    __tablename__ = 'docking_bays'
    id = Column(Integer, primary_key=True)
    bay_number = Column(String)
    spaceport_id = Column(Integer, ForeignKey('spaceports.id'))
    
    spaceport = relationship("Spaceport", back_populates="docking_bays")

class SmugglerFaction(Base):
    __tablename__ = 'smuggler_factions'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    missions = relationship("TransportMission", secondary=mission_faction_table, back_populates="factions")

class TransportMission(Base):
    __tablename__ = 'transport_missions'
    id = Column(Integer, primary_key=True)
    tracking_code = Column(String)
    destination_id = Column(Integer, ForeignKey('planet_locations.id'))
    origin_spaceport_id = Column(Integer, ForeignKey('spaceports.id'))
    
    destination = relationship("PlanetLocation")
    origin_spaceport = relationship("Spaceport", back_populates="missions")
    factions = relationship("SmugglerFaction", secondary=mission_faction_table, back_populates="missions")