from flask import Blueprint, render_template, redirect, url_for, flash, request
from models import Show, Venue, db, Artist
from flask_wtf import form
from forms import *

venue_bp = Blueprint('venue_bp', __name__, template_folder='templates')

@venue_bp.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  result = Venue.query.all()
  dist_venues = Venue.query.distinct(Venue.state, Venue.city).all()

  dataReturn = []
  current = datetime.now()
  for dist in dist_venues:
    venue_city = {
      "city": dist.city,
      "state": dist.state,
      "venues" : []
    }

    for ven in result:
      if (dist.city == ven.city and dist.state == ven.state):
        venue_city['venues'].append({
          "id": ven.id,
          "name": ven.name,
          "state": ven.state,
          "num_upcoming_shows": len([show for show in ven.shows if show.start_time>current])
        })
    dataReturn.append(venue_city)


  #print(dataReturn)
  if len(dataReturn) == 0:
    flash('Oops! No venue created at the moment')
  # past_show_query = db.session.query(Show).join(Venue).filter(Show.artist_id==Artist.id).filter(Show.start_time<datetime.now()).all()
  #print(past_show_query)
  # for res in past_show_query:
  #   result.append()

  return render_template('venues/venues.html', areas=dataReturn);

@venue_bp.route('/venues/search', methods=['POST'])
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
  return render_template('venues/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@venue_bp.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  result = Venue.query.filter(Venue.id == venue_id).first()
  past_show_query = db.session.query(Show).join(Venue).filter(Show.artist_id==Artist.id).filter(Show.start_time<datetime.now()).all()
  num_past_show = len(past_show_query)
  upcoming_show_query = db.session.query(Show).outerjoin(Venue).filter(Show.artist_id==Artist.id).filter(Show.start_time>datetime.now()).all()
  num_upcoming_show = len(upcoming_show_query)

  #print(upcoming_show_query[0].artists.name)





  return render_template('venues/show_venue.html', venue=result, past=num_past_show, current=num_upcoming_show, upcoming=upcoming_show_query, past_shows=past_show_query)

#  Create Venue
#  ----------------------------------------------------------------

@venue_bp.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@venue_bp.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  venue = VenueForm(request.form) 
  error=False
  checker=False
  match = None
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

    us_phone_num = '^([0-9]{3})[-][0-9]{3}[-][0-9]{4}$'
    match = re.search(us_phone_num, phone)
    if match is not None :
      venue = Venue(name=names, city=city, state=state, phone=phone, address=addr, genres=genres, facebook_link=facebook_link, image_link=image_link, website_link=website, seeking_talent=talent, seeking_description=desc)
      db.session.add(venue)
      db.session.commit() 
    else:
      error=True
      flash("Invalid phone number. Make sure you input valid digits following this pattern xxx-xxx-xxxx to enter your digits")
    
      
  except:
      db.session.rollback()
      error=True
  finally:
      db.session.close()

  

  # on successful db insert, flash success
  
  if match is not None:
    if not error :
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    else:
      flash(f'Venue creation failed! this may occur if phone number{phone} already exist or internal server issue')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@venue_bp.route('/venues/<venue_id>/delete', methods=['DELETE'])
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


@venue_bp.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  
  result = Venue.query.filter(Venue.id == venue_id).first()
  form = VenueForm(obj=result)
 
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=result)

@venue_bp.route('/venues/<int:venue_id>/edit', methods=['POST'])
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

      us_phone_num = '^([0-9]{3})[-][0-9]{3}[-][0-9]{4}$'
      match = re.search(us_phone_num, v4)
      if match is not None :
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
      flash("Venue updated successfully!")
    else:
      flash("Failed to update Venue fields")
  
 
  return redirect(url_for('venue_bp.show_venue', venue_id=venue_id))

