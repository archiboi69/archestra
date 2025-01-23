from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry
from sqlalchemy.dialects.postgresql import JSONB

db = SQLAlchemy()

class Site(db.Model):
    """Represents a potential development site."""
    __tablename__ = 'sites'
    
    id = db.Column(db.Integer, primary_key=True)
    id_egib = db.Column(db.String, unique=True, nullable=False)  # '226101_1.0042.652/12'
    district = db.Column(db.String)  # 'NAZWA_OBREBU'
    geometry = db.Column(Geometry('MULTIPOLYGON', srid=2177))
    area = db.Column(db.Float, nullable=False)
    shape_index = db.Column(db.Float)
    
    # Road access info
    access_road_id = db.Column(db.String)  # ID_DZIALKI of the road plot
    access_road_name = db.Column(db.String)  # nazwa_ulicy
    frontage_length = db.Column(db.Float)
    
    # Development metrics
    metrics = db.Column(JSONB)  # Current metrics {far, bcr, setback, max_height, max_front_width}
    dev_conditions = db.Column(JSONB)  # Development conditions {far, bcr, setback, max_height, max_front_width}
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_calculated = db.Column(db.DateTime)
    data_version = db.Column(db.Integer, default=1)
    
    # Relationships
    buildings = db.relationship('Building', back_populates='site', cascade='all, delete-orphan')

class Building(db.Model):
    """Represents existing buildings."""
    __tablename__ = 'buildings'
    
    id = db.Column(db.Integer, primary_key=True)
    id_egib = db.Column(db.String)  # IDEGIB from BDOT10k
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=False)
    geometry = db.Column(Geometry('MULTIPOLYGON', srid=2177))
    
    # Building characteristics
    area = db.Column(db.Float)
    stories = db.Column(db.Integer)  # LICZBAKONDYGNACJI
    height = db.Column(db.Float)
    front_width = db.Column(db.Float)
    kst_class = db.Column(db.String)  # KODKST
    function = db.Column(db.String)  # FUNKCJAOGOLNABUDYNKU
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_calculated = db.Column(db.DateTime)
    data_version = db.Column(db.Integer, default=1)
    
    # Relationships
    site = db.relationship('Site', back_populates='buildings')
