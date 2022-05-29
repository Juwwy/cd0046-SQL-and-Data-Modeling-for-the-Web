#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#



from email.policy import default
from enum import unique
import json
from pydoc import describe
import sys
import dateutil.parser
import babel
from flask import Flask, abort, jsonify, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import form
from sqlalchemy import PickleType, desc
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)


migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


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



# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  result_artists = Artist.query.order_by(Artist.id.desc()).limit(10).all()
  result_venues = Venue.query.order_by(Venue.id.desc()).limit(10).all()


  
  return render_template('pages/home.html', artists=result_artists, data=result_venues)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  result = Venue.query.all()

  return render_template('pages/venues.html', areas=result);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  searchVal = form.request.form['search_term']

  searchResult = Venue.query.filter(Venue.name.ilike(f'%{searchVal}%')).all()
  total = len(searchResult)

  response={
    "count": total,
    "data": searchResult
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  result = Venue.query.filter(Venue.id == venue_id).first()
  return render_template('pages/show_venue.html', venue=result)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  venue = VenueForm(request.form) 
  error=False
  try:
    
      names= venue.name.data
      city= venue.city.data
      state= venue.state.data
      phone= venue.phone.data
      addr = venue.address.data
      genres= venue.genres.data
      facebook_link= venue.facebook_link.data
      image_link = venue.image_link.data
      website= venue.website_link.data
      talent= venue.seeking_talent.data 
      desc = venue.seeking_description.data

      venue = Venue(name=names, city=city, state=state, phone=phone, address=addr, genres=genres, facebook_link=facebook_link, image_link=image_link, website_link=website, seeking_talent=talent, seeking_description=desc)
      db.session.add(venue)
      db.session.commit()
  except:
      db.session.rollback()
      error=True
      print(sys.exc_info())
  finally:
      db.session.close()

  

  # on successful db insert, flash success
  
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  else:
    flash(f'Venue creation failed! this may occur if phone number already exist or internal server issue')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:

    db.session.query(Venue).filter(Venue.id == venue_id).delete()
    db.session.commit()
  except Exception as error:
    print(error)
    db.session.rollback()
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  
  result = Venue.query.filter(Venue.id == venue_id).first()
  form = VenueForm(obj=result)
 
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=result)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  error=False

  venue = VenueForm(request.form) 
  v1 = venue.name.data
  v2 = venue.city.data
  v3 = venue.state.data
  v4 = venue.phone.data
  v5 = venue.address.data
  v6 = venue.genres.data
  v7 = venue.facebook_link.data
  v8 = venue.image_link.data
  v9 = venue.website_link.data
  v10 = venue.seeking_talent.data
  v11 = venue.seeking_description.data
  
  try:
    db.session.query(Venue).filter(Venue.id == venue_id).update({
      'name': v1,
      'city' : v2,
      'state' : v3,
      'phone' : v4,
      'address' : v5,
      'genres' : v6,
      'facebook_link' : v7,
      'image_link' : v8,
      'website_link' : v9,
      'seeking_talent' : v10,
      'seeking_description' : v11
      })
    db.session.commit()
  except:
    error=True
    db.session.rollback()
  finally:
    db.session.close()


  if not error:
    flash("Venue updated successfully!")
  else:
    flash("Failed to update Venue fields")
  
 
  return redirect(url_for('show_venue', venue_id=venue_id))





#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  result = Artist.query.all()

  return render_template('pages/artists.html', artists=result)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  searchVal = form.request.form['search_term']
  searchResult = Artist.query.filter(Artist.name.ilike(f'%{searchVal}%')).all()


  total = len(searchResult)

  response={
    "count": total,
    "data": searchResult
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  result = Artist.query.filter(Artist.id == artist_id).first()
  
  
  print(result.name)
  return render_template('pages/show_artist.html', artist=result)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  result = Artist.query.get(artist_id)
  form = ArtistForm(obj=result)

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=result)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = ArtistForm(request.form)
  a1 = artist.name.data
  a2 = artist.city.data
  a3 = artist.state.data
  a4 = artist.phone.data
  a6 = artist.genres.data
  a7 = artist.facebook_link.data
  a8 = artist.image_link.data
  a9 = artist.website_link.data
  a10 = artist.seeking_venue.data
  a11 = artist.seeking_description.data

  error=False

  try:
    db.session.query(Artist).filter(Artist.id == artist_id).update({
      'name': a1,
      'city' : a2,
      'state' : a3,
      'phone' : a4,
      'genres' : a6,
      'facebook_link' : a7,
      'image_link' : a8,
      'website_link' : a9,
      'seeking_venue' : a10,
      'seeking_description' : a11
      })
    db.session.commit()
  except:
    error=True
    db.session.rollback()
  finally:
    db.session.close()

  if not error:
    flash("Artist updated successfully!")
  else:
    flash("Failed to update Artist fields")

  return redirect(url_for('show_artist', artist_id=artist_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  error=False
  artist = ArtistForm(request.form)
  errVal = ""

  try:
    names= artist.name.data
    city= artist.city.data
    state= artist.state.data
    phone= artist.phone.data
    genres= artist.genres.data
    facebook_link= artist.facebook_link.data
    image_link = artist.image_link.data
    website= artist.website_link.data
    venue= artist.seeking_venue.data 
    desc = artist.seeking_description.data

    artist= Artist(name=names, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website_link=website, seeking_venue=venue, seeking_description=desc)
    
    db.session.add(artist)
    db.session.commit()
  except Exception as err:
    errVal = err
    error=True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  
  # on successful db insert, flash success
  if not error:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  else:
    flash(f'Artist creation failed! this may occur if phone number already exist or internal server issue')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    
  return render_template('pages/home.html')

@app.route('/artists/<artist_id>/delete', methods=['DELETE'])
def delete_artist(artist_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:

    db.session.query(Artist).filter(Artist.id == artist_id).delete()
    db.session.commit()
  except Exception as error:
    print(error)
    db.session.rollback()
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  #flash('Artist deleted successfully!')
  
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  result = Show.query.outerjoin(Artist, Show.artist_id == Artist.id).outerjoin(Venue, Show.venue_id == Venue.id).all()
  

  print(result)
  return render_template('pages/shows.html', shows=result)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  show = ShowForm(request.form)
  error=False
  
  try:
    artist_id = show.artist_id.data
    venue_id = show.venue_id.data
    start_time = show.start_time.data

    #===========Validation ===========
    checkArtist = Artist.query.filter(Artist.id == artist_id).first()
    checkVenue = Venue.query.filter(Venue.id == venue_id).first()

    print(checkArtist, checkVenue)
    if not None in (checkArtist, checkVenue): 
      shows = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
      db.session.add(shows)
      db.session.commit()
      flash('Show was successfully listed!')
    else:
      flash("Oops! there was an error while creating shows. Make sure you insert respective IDs correctly ", 'error')
      
  except:
    error=True
    db.session.rollback()
  finally:
    db.session.close()
    

  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
