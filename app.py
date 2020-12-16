#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment # Formatting of dates and times in Flask templates 
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from sqlalchemy.orm import backref
from forms import *
from flask_migrate import Migrate
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120), nullable=False)

    # database migration
    genres = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(252))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(252))
    
    # relate to Show Table with id
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
      return f'<Venue id: {self.id}, name: {self.name}, city: {self.city} \
                      state: {self.state}, address: {self.address}, phone: {self.phone},\
                      image_link: {self.image_link}, facebook_link: {self.facebook_link},\
                      genres: {self.genres}, website: {self.website}, seeking_talent: {self.seeking_talent},\
                      seeking_description: {self.seeking_description}>'


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120), nullable=False, default=False)

    # database migration
    website = db.Column(db.String(252))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(252), nullable=True)

    # relate to Show Table with id
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
      return f'<Artist id: {self.id}, name: {self.name}, city: {self.city} \
                  state: {self.state}, phone: {self.phone},image_link: {self.image_link},\
                  facebook_link: {self.facebook_link},genres: {self.genres}, website: {self.website},\
                  seeking_venue: {self.seeking_venue},seeking_description: {self.seeking_description}>'

class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)

    def __repr__(self):
      return f'<Show id: {self.id}, start_time: {self.start_time},\
              artist_id: {self.artist_id}, venue_id: {self.venue_id}>'
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  """
    view venues list and group by city
    Parameters:
        Null
    Returns:
        render_template (Object) : html template for flask 
  """
  data = []
  city_state_groups = Venue.query.with_entities(Venue.city, Venue.state).distinct().all() 
  # check all city and state union
  for city_state in city_state_groups:
    venues_group = []
    city = city_state[0]
    state = city_state[1]
    # Filter by city and state 
    venues = Venue.query.filter_by(city=city, state=state).all() 
    for venue in venues:
      upcoming_shows = [show for show in venue.shows if show.start_time > datetime.now()]
      # Group data 
      venues_group.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": len(upcoming_shows)
      })

    data.append({
      'city': city,
      'state': state,
      'venues': venues_group
      })
    print('data',data)

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  """
    Search a venue from the database
    Parameters:
        Null
    Returns:
        render_template (Object) : html template for flask 
  """
  data = []
  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%'))
  for venue in venues:
    upcoming_shows = [show for show in venue.shows if show.start_time > datetime.now()]
    data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": upcoming_shows
    })

  response = {
    "count" : len(data),
    "data" : data
  }

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  """
    view a venue
    Parameters:
        venue_id (Integer) : venue id 
    Returns:
        render_template (Object) : html template for flask 
  """
  venue = Venue.query.get(venue_id)
  if not venue:
    flash('Venue Missing')   
    return redirect('/venues')
  
  past_shows_group = [show for show in venue.shows if show.start_time <= datetime.now()]
  upcoming_shows_group = [show for show in venue.shows if show.start_time > datetime.now()]

  num_past_shows = len(past_shows_group)
  num_upcoming_shows = len(upcoming_shows_group)

  # Get past shows 
  past_shows = []
  for show in past_shows_group:
      artist = Artist.query.get(show.artist_id)
      past_shows.append({
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": str(show.start_time)
      })
  # Get upcoming shows
  upcoming_shows = []
  for show in upcoming_shows_group:
    artist = Artist.query.get(show.artist_id)
    upcoming_shows.append({
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": str(show.start_time)
    })
  # Package  
  data = {
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent, 
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link if venue.image_link else "",
      "past_shows_count": num_past_shows,
      "upcoming_shows_count": num_upcoming_shows,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  """
    route to the create venue page
  """
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  """
    Create a venue and INSERT into database
    Parameters:
        Null
    Returns:
        render_template (Object) : html template for flask 
  """
  error = False
  try:
    venues = Venue(
      name = request.form.get('name'),  
      city = request.form.get('city'),
      state = request.form.get('state'),
      address = request.form.get('address'),
      phone = request.form.get('phone'),  
      genres = request.form.getlist('genres'),
      facebook_link = request.form.get('facebook_link'),
      website = request.form.get('website'),
      image_link = request.form.get('image_link'),
      seeking_talent = True if request.form.get('seeking_talent') == 'y' else False , 
      seeking_description = request.form.get('seeking_description','')
    )
    print(venues)
    db.session.add(venues)
    db.session.commit()

  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
    # on unsuccessful db insert, flash error 
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  
  finally:
    db.session.close()
  
  if error:
    abort(500)
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  """
    Delete a venue from database
    Parameters:
        venue_id (Integer) : venue id
    Returns:
        None
  """
  error = False
  venue = Venue.query.get(venue_id)

  try:
    db.session.delete(venue)
    db.session.commit()

  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
    # on unsuccessful db insert, flash error 
    flash('An error occurred. Venue ' + venue.name + ' could not be deleted!')

  finally:
    db.session.close()
  
  if error:
        abort(500)
  else:
     # on successful db delete, flash success
    flash('Venue ' + venue.name + ' was successfully deleted!')
    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  """
    view venues list and group by city
    Parameters:
        None
    Returns:
        render_template (Object) : html template for flask 
  """
  artists = Artist.query.with_entities(Artist.id, Artist.name).all()
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  """
    search a artist by search term
    Parameters:
        None
    Returns:
        render_template (Object) : html template for flask 
  """
  data = []
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).all()

  for artist in artists:
    upcoming_shows = [show for show in artist.shows if show.start_time > datetime.now()]
    data.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": len(upcoming_shows)
    })

  response={
    "count": len(artists),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  """
    show a artist by artist id
    Parameters:
        artist_id (Integer)
    Returns:
        render_template (Object) : html template for flask 
  """
  # Select a artist by id
  artist = Artist.query.get(artist_id)
 

  past_shows_group = [show for show in artist.shows if show.start_time <= datetime.now()]
  upcoming_shows_group = [show for show in artist.shows if show.start_time > datetime.now()]

  num_past_shows = len(past_shows_group)
  num_upcoming_shows = len(upcoming_shows_group)


  # Get upcoming shows
  upcoming_shows = []
  for show in upcoming_shows_group:
    venue = Venue.query.get(show.venue_id)
    upcoming_shows.append({
        "venue_id": venue.id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": str(show.start_time)
  })

  # Get past shows
  past_shows = []
  for show in past_shows_group:    
    venue = Venue.query.get(show.venue_id)
    past_shows.append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": str(show.start_time)
  })

  data = {
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link, 
      "facebook_link": artist.facebook_link,
      "website_link": artist.website,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": num_past_shows,
      "upcoming_shows_count": num_upcoming_shows
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  """
    Set data for editing
    Parameters:
        artist_id (Integer)
    Returns:
        render_template (Object) : html template for flask 
  """
  artist = Artist.query.get(artist_id)
  form = ArtistForm()
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(';'),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "facebook_link": artist.facebook_link,
    "website": artist.website,
    }

  return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  """
    edit a artist by artist id
    Parameters:
        artist_id (Integer)
    Returns:
        render_template (Object) : html template for flask 
  """
  error = False
  artist = Artist.query.get(artist_id)

  artist.name = request.form.get('name')
  artist.city = request.form.get('city')
  artist.state = request.form.get('state')
  artist.phone = request.form.get('phone')
  artist.genres = request.form.getlist('genres')
  artist.image_link = request.form.get('image_link')
  artist.facebook_link = request.form.get('facebook_link')
  artist.website = request.form.get('website')
  artist.seeking_venue = True if request.form.get('seeking_venue')=='y' else False
  artist.seeking_description = request.form.get('seeking_description','')
  
  try:
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    
  except:
    error = True
    print(sys.exc_info())
    # on unsuccessful db insert, flash error 
    flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
    db.session.rollback()
    db.session.close()

  finally:
    db.session.close()

  if error:
    abort(500)
  else:
    return redirect(url_for('show_artist', artist_id=artist_id))



@app.route('/venues/<int:artist_id>/edit', methods=['GET'])
def edit_venue(artist_id):
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(artist_id):
  artist = Artist.query.get(artist_id)

  try:
    artist = Artist(
      name = request.form.get('name'),  
      city = request.form.get('city'),
      state = request.form.get('state'),
      phone = request.form.get('phone'),  
      genres = request.form.getlist('genres'),
      facebook_link = request.form.get('facebook_link'),
      website = request.form.get('website'),
      image_link = request.form.get('image_link'),
      seeking_venue = True if request.form.get('seeking_venue') == 'y' else False , 
      seeking_description = request.form.get('seeking_description','')
    )
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
      
  except:
    flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
    db.session.rollback()
    db.session.close()
  
  finally:
    db.session.close()
    return redirect(url_for('show_venue', artist_id=artist_id))
  

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  """
    route to the create artist page
  """
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  """
    Create a artist and INSERT into database
    Parameters:
        Null
    Returns:
        render_template (Object) : html template for flask 
  """
  error = False
  try:
    artist = Artist(
      name = request.form.get('name'),  
      city = request.form.get('city'),
      state = request.form.get('state'),
      phone = request.form.get('phone'),  
      genres = request.form.getlist('genres'),
      facebook_link = request.form.get('facebook_link'),
      website = request.form.get('website'),
      image_link = request.form.get('image_link'),
      seeking_venue = True if request.form.get('seeking_venue') == 'y' else False , 
      seeking_description = request.form.get('seeking_description','')
    )
    print(artist)
    db.session.add(artist)
    db.session.commit()
  
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
    # on unsuccessful db insert, flash error 
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  
  finally:
    db.session.close()
  
  if error:
    abort(500)
  else:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  """
    Shows list
    Parameters:
        Null
    Returns:
        render_template (Object) : html template for flask 
  """
  data=[]
  # join table by id and set Venue.name as venue_name, Artist.name as artist_name 
  shows_query = Show.query.join(Venue, (Venue.id == Show.venue_id))\
                    .join(Artist, (Artist.id == Show.artist_id))\
                    .with_entities(Show.artist_id, Artist.name.label('artist_name'),\
                                   Show.venue_id, Venue.name.label('venue_name'),\
                                   Artist.image_link,\
                                   Show.start_time)
  
  for show in shows_query:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue_name,
      "artist_id": show.artist_id,
      "artist_name": show.artist_name,
      "artist_image_link": show.image_link,
      "start_time": str(show.start_time)
    })
  return render_template('pages/shows.html', shows=data)
 

@app.route('/shows/create')
def create_shows():
  """
    route to the create a show page
  """
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  """
    Create a show and INSERT into database
    Parameters:
        Null
    Returns:
        render_template (Object) : html template for flask 
  """
  error = False
  # check id is exeist
  venue_id = request.form.get('venue_id'),
  artist_id = request.form.get('artist_id')

  artist = Artist.query.filter_by(id = artist_id).first()
  venue = Venue.query.filter_by(id = venue_id).first()

  if not artist and venue:
    flash('Wrong id')
    return redirect('/shows/create')

  try:
    show = Show(
      start_time = request.form.get('start_time'),
      venue_id = venue_id,
      artist_id = artist_id
    )
    print(show)
    db.session.add(show)
    db.session.commit()
  
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
    # on unsuccessful db insert, flash error 
    flash('An error occurred. Show could not be listed.')
  
  finally:
    db.session.close()
  
  if error:
    abort(500)
  else:
    # on successful db insert, flash success
    flash('Show was successfully listed!')
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
