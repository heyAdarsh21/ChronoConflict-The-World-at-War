"""
Database models for WW2 Intelligence Operations Simulator
"""

from database import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship

class User(db.Model):
    """User accounts for saving progress"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default='historian')  # 'historian' or 'commander'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    simulations = relationship('Simulation', backref='user', lazy=True)

class Battle(db.Model):
    """Historical battle records"""
    __tablename__ = 'battles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    location = Column(String(200))
    axis_forces = Column(Integer)
    allied_forces = Column(Integer)
    axis_casualties = Column(Integer)
    allied_casualties = Column(Integer)
    victor = Column(String(20))  # 'axis' or 'allies'
    description = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)
    
    operations = relationship('Operation', backref='battle', lazy=True)

operation_tactics = Table(
    'operation_tactics',
    db.metadata,
    Column('operation_id', Integer, ForeignKey('operations.id'), primary_key=True),
    Column('tactic_id', Integer, ForeignKey('tactics.id'), primary_key=True)
)


class Operation(db.Model):
    """Military operations and campaigns"""
    __tablename__ = 'operations'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    code_name = Column(String(100))
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    side = Column(String(20))  # 'axis' or 'allies'
    objective = Column(Text)
    outcome = Column(String(50))  # 'success', 'failure', 'partial'
    battle_id = Column(Integer, ForeignKey('battles.id'))
    description = Column(Text)
    region = Column(String(100))  # Europe, Pacific, etc.
    campaign_id = Column(Integer, ForeignKey('campaigns.id'))
    objectives_detail = Column(Text)  # JSON string of detailed objectives
    participating_nations = Column(Text)  # JSON string
    casualties_axis = Column(Integer)
    casualties_allies = Column(Integer)
    resources_fuel = Column(Float)
    resources_aircraft = Column(Integer)
    resources_naval = Column(Integer)
    analysis = Column(Text)  # Strategic analysis narrative
    tactics_summary = Column(Text)
    map_overlay = Column(String(255))  # Path to GeoJSON or image
    intelligence_notes = Column(Text)
    
    commander_assignments = relationship('CommandAssignment', back_populates='operation', cascade='all, delete-orphan')
    tactics = relationship('Tactic', secondary=operation_tactics, back_populates='operations', lazy='dynamic')

class Resource(db.Model):
    """Resource data by nation and date"""
    __tablename__ = 'resources'
    
    id = Column(Integer, primary_key=True)
    nation = Column(String(50), nullable=False)  # 'Germany', 'USA', 'USSR', etc.
    date = Column(DateTime, nullable=False)
    oil = Column(Float)
    steel = Column(Float)
    manpower = Column(Integer)
    gdp = Column(Float)
    morale = Column(Float)  # 0-100
    territory_count = Column(Integer)

class Territory(db.Model):
    """Territorial control data"""
    __tablename__ = 'territories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    controlled_by = Column(String(50))  # Nation name
    date_controlled = Column(DateTime)
    strategic_value = Column(Integer)  # 1-10
    region = Column(String(100))  # 'Europe', 'Pacific', 'Africa', etc.

class IntelligenceReport(db.Model):
    """Intelligence and intercepted messages"""
    __tablename__ = 'intelligence_reports'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow)
    classification = Column(String(20))  # 'top_secret', 'secret', 'confidential'
    source = Column(String(100))  # 'radio_intercept', 'spy', 'decrypt'
    content = Column(Text, nullable=False)
    decoded = Column(Boolean, default=False)
    side = Column(String(20))  # 'axis' or 'allies'
    location = Column(String(200))

class Simulation(db.Model):
    """User simulation sessions"""
    __tablename__ = 'simulations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    scenario_name = Column(String(200))
    start_year = Column(Integer)
    side = Column(String(20))  # 'axis' or 'allies'
    decisions = Column(Text)  # JSON string of decisions made
    outcome = Column(Text)  # JSON string of results
    created_at = Column(DateTime, default=datetime.utcnow)
    completed = Column(Boolean, default=False)


class Leader(db.Model):
    """Political and military leaders"""
    __tablename__ = 'leaders'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    country = Column(String(100), nullable=False)
    title = Column(String(150))
    role_type = Column(String(50))  # political, military, diplomatic
    biography = Column(Text)
    ideology = Column(Text)
    portrait_url = Column(String(255))
    notable_quotes = Column(Text)  # JSON list
    key_operations = Column(Text)  # JSON list
    influence_score = Column(Float)
    born = Column(DateTime)
    died = Column(DateTime)

    assignments = relationship('CommandAssignment', back_populates='leader', cascade='all, delete-orphan')


class CommandAssignment(db.Model):
    """Link leaders to operations and campaigns"""
    __tablename__ = 'command_assignments'

    id = Column(Integer, primary_key=True)
    leader_id = Column(Integer, ForeignKey('leaders.id'), nullable=False)
    operation_id = Column(Integer, ForeignKey('operations.id'))
    campaign_id = Column(Integer, ForeignKey('campaigns.id'))
    position = Column(String(150))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    notes = Column(Text)

    leader = relationship('Leader', back_populates='assignments')
    operation = relationship('Operation', back_populates='commander_assignments')
    campaign = relationship('Campaign', back_populates='command_assignments')


class Campaign(db.Model):
    """Military campaigns grouping operations"""
    __tablename__ = 'campaigns'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    theater = Column(String(100))  # Europe, Pacific, etc.
    region = Column(String(100))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    description = Column(Text)
    outcome = Column(String(50))
    strategic_value = Column(Integer)

    operations = relationship('Operation', backref='campaign', lazy=True)
    command_assignments = relationship('CommandAssignment', back_populates='campaign', cascade='all, delete-orphan')


class WarCrime(db.Model):
    """War crimes and humanitarian atrocities"""
    __tablename__ = 'war_crimes'

    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    event_date = Column(DateTime)
    end_date = Column(DateTime)
    location = Column(String(200))
    region = Column(String(100))
    perpetrators = Column(Text)
    victims = Column(Text)
    death_toll = Column(Integer)
    description = Column(Text)
    sources = Column(Text)  # JSON list of citations
    media_url = Column(String(255))
    category = Column(String(100))  # genocide, pow_abuse, bombing, etc.


class EconomicStat(db.Model):
    """Economic and industrial data"""
    __tablename__ = 'economic_stats'

    id = Column(Integer, primary_key=True)
    country = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    gdp = Column(Float)
    military_spending = Column(Float)
    production_tanks = Column(Integer)
    production_aircraft = Column(Integer)
    production_ships = Column(Integer)
    production_artillery = Column(Integer)
    trade_balance = Column(Float)
    inflation_index = Column(Float)
    war_debt = Column(Float)
    strain_index = Column(Float)
    notes = Column(Text)


class Tactic(db.Model):
    """Military tactics and doctrines"""
    __tablename__ = 'tactics'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    domain = Column(String(50))  # land, air, naval, intelligence
    description = Column(Text)
    period_start = Column(Integer)
    period_end = Column(Integer)
    doctrine_notes = Column(Text)
    visualization_svg = Column(String(255))
    innovation_highlights = Column(Text)  # JSON list of innovations

    operations = relationship('Operation', secondary=operation_tactics, back_populates='tactics')


class MilitaryInnovation(db.Model):
    """Timeline of technological innovations"""
    __tablename__ = 'military_innovations'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    category = Column(String(50))  # weapon, technology, intelligence
    description = Column(Text)
    nation = Column(String(100))
    year = Column(Integer)
    image_url = Column(String(255))
    notes = Column(Text)


