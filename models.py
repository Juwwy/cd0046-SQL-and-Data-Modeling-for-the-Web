from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
from forms import *


app = Flask(__name__)
db = SQLAlchemy(app)

migrate = Migrate(app, db)

class Show(db.Model):
  __tablename__ = 'shows'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id', ondelete='CASCADE'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id', ondelete='CASCADE' ), nullable=False)
  start_time = db.Column( db.DateTime, nullable=False, default=datetime.utcnow() )


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False, unique=True)
    image_link = db.Column(db.String(500), nullable=False)
    genres = db.Column( db.PickleType, default=[], nullable=False)
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(200), nullable=True)
    website_link = db.Column(db.String(50), nullable=True)

    shows = db.relationship('Show', backref=db.backref('venues', lazy='joined'), lazy='joined', cascade="all, delete-orphan")

    def  __repr__(self):
      return f'<Venue: {self.name}, {self.city}, {self.state}, {self.address}, {self.phone}, {self.genres}>'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False, unique=True)
    genres = db.Column( db.PickleType, default=[], nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(200), nullable=True)
    website_link = db.Column(db.String(50), nullable=True)
    shows = db.relationship('Show', backref=db.backref('artists', lazy='joined'), lazy='joined', cascade="all, delete-orphan")


    def  __repr__(self):
      return f'<Artist: {self.name}, {self.city}, {self.state}, {self.phone}, {self.genres}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate