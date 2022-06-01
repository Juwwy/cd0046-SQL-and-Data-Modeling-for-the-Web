from flask import Blueprint, render_template, redirect, url_for, flash, request
from models import Artist, db, Show, Venue
from flask_wtf import form
from forms import *

artist_bp = Blueprint('artist_bp', __name__, template_folder='templates')


@artist_bp.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  result = Artist.query.all()

  return render_template('artists/artists.html', artists=result)

@artist_bp.route('/artists/search', methods=['POST'])
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
  return render_template('artists/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@artist_bp.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  result = Artist.query.filter(Artist.id == artist_id).first()
  
  past_show_query = db.session.query(Show).join(Artist).filter(Show.venue_id==Venue.id).filter(Show.start_time<datetime.now()).all()
  num_past_show = len(past_show_query)
  upcoming_show_query = db.session.query(Show).outerjoin(Artist).filter(Show.venue_id==Venue.id).filter(Show.start_time>datetime.now()).all()
  num_upcoming_show = len(upcoming_show_query)
  
  
  print(past_show_query)
  return render_template('artists/show_artist.html', artist=result, past=num_past_show, current=num_upcoming_show, upcoming=upcoming_show_query, past_shows=past_show_query)

#  Update
#  ----------------------------------------------------------------
@artist_bp.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  result = Artist.query.get(artist_id)
  form = ArtistForm(obj=result)

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=result)

@artist_bp.route('/artists/<int:artist_id>/edit', methods=['POST'])
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
            us_phone_num = '^([0-9]{3})[-][0-9]{3}[-][0-9]{4}$'
            match = re.search(us_phone_num, a4)
        
            if match is not None :
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
            else:
                error=True
                flash("Invalid phone number. Make sure you input valid digits following this pattern xxx-xxx-xxxx to enter your digits") 
  except:
        error=True
        db.session.rollback()
  finally:
        db.session.close()

  if match is not None:
    if not error:
        flash("Artist updated successfully!")
    else:
        flash("Failed to update Artist fields")

  return redirect(url_for('artist_bp.show_artist', artist_id=artist_id))

#  Create Artist
#  ----------------------------------------------------------------

@artist_bp.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@artist_bp.route('/artists/create', methods=['POST'])
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


    us_phone_num = '^([0-9]{3})[-][0-9]{3}[-][0-9]{4}$'
    match = re.search(us_phone_num, phone)
    if match is not None :
       artist= Artist(name=names, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website_link=website, seeking_venue=venue, seeking_description=desc)
       db.session.add(artist)
       db.session.commit() 
    else:
      error=True
      flash("Invalid phone number. Make sure you input valid digits following this pattern xxx-xxx-xxxx to enter your digits")
  except Exception as err:
    errVal = err
    error=True
    db.session.rollback()
  finally:
    db.session.close()

  
  # on successful db insert, flash success
  if match is not None:
    if not error:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    else:
        flash(f'Artist creation failed! this may occur if phone number {phone} already exist or internal server issue')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    
  return render_template('pages/home.html')

@artist_bp.route('/artists/<artist_id>/delete', methods=['DELETE'])
def delete_artist(artist_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:

    db.session.query(Artist).filter(Artist.id == artist_id).delete()
    db.session.commit()
  except Exception as error:
    #print(error)
    db.session.rollback()
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  #flash('Artist deleted successfully!')
  
  return render_template('pages/home.html')

