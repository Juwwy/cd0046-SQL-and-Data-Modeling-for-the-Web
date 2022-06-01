from flask import Blueprint, render_template, redirect, url_for, flash, request
from models import Show, db, Artist, Venue
from flask_wtf import form
from forms import *

show_bp = Blueprint('show_bp', __name__, template_folder='templates')


@show_bp.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  result = Show.query.outerjoin(Artist, Show.artist_id == Artist.id).outerjoin(Venue, Show.venue_id == Venue.id).all()
  

 # print(result)
  return render_template('shows/shows.html', shows=result)

@show_bp.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@show_bp.route('/shows/create', methods=['POST'])
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

    #print(checkArtist, checkVenue)
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

@show_bp.route('/venues/search', methods=['POST'])
def search_shows():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  result = Show.query.outerjoin(Artist, Show.artist_id == Artist.id).outerjoin(Venue, Show.venue_id == Venue.id).all()
  searchVal = form.request.form['search_term']
  res =result.query.filter(result.artists.name.ilike(f'%{searchVal}%')).all()
  if res is None:
      res =result.query.filter(result.venues.name.ilike(f'%{searchVal}%')).all()

  searchResult = Venue.query.filter(result.name.ilike(f'%{searchVal}%')).all()
  total = len(res)
  print(res)

  response={
    "count": total,
    "data": res
  }
  return render_template('venues/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


