#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:type_yourserver_password@localhost:5432/venuesapp'
#---------------------------------------------------------------------------#
# migrations
migrate=Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Shows(db.Model):
    #__tablename__= 'Shows'
    __tablename__='shoows'
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    start_time=db.Column(db.Date,nullable=False)
    venue_id=db.Column(db.Integer,db.ForeignKey('Venue.id'),primary_key=True)
    artist_id=db.Column(db.Integer,db.ForeignKey('Artist.id'),primary_key=True)
    def __repr__(self):
      return f'<shows_id: {self.id}, start_time: {self.start_time}, venue_id: {self.venue_id}, artist_id: {self.artist_id}>'
    
class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120),nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    address = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120),nullable=False)
    image_link = db.Column(db.String(500),nullable=True)
    facebook_link = db.Column(db.String(120),nullable=True)
    #---missing fields in table Venue-----------------#
    genres=db.Column(db.String(500),nullable=False)
    website=db.Column(db.String(120),nullable=True)
    seeking_talent=db.Column(db.Boolean,default=False)
    seeking_description=db.Column(db.String(500),default='')  
    artists = db.relationship('Artist', secondary='shoows',backref=db.backref('venues', lazy=True))
    def __repr__(self):
      return f'<venue_id: {self.id}, name: {self.name} , city: {self.city}, state: {self.state}, address: {self.address}, phone: {self.phone}, genres: {self.genres}>'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120),nullable=False)
    genres = db.Column(db.String(120),nullable=False)
    image_link = db.Column(db.String(500),nullable=True)
    facebook_link = db.Column(db.String(120),nullable=True)
    #---- missing fields in Artist table -----------------------------------#
    website=db.Column(db.String(),nullable=True)
    seeking_venue=db.Column(db.Boolean,default=False)
    seeking_description=db.Column(db.String(500),default='')

    def __repr__(self):
      return f'<Artist_id: {self.id}, name:{self.name}, city:{self.city}, state:{self.state} ,phone:{self.phone}, genres:{self.genres}>'
    #artist_shows = db.relationship('Shows', back_populates='artist', lazy=True)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
#db.create_all()
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
  return babel.dates.format_datetime(date, format,locale='en')

app.jinja_env.filters['datetime'] = format_datetime

def compare_date(value):
  value=str(value)
  time_value=datetime.datetime.strptime(value, '%Y-%m-%d')
  time_now = datetime.datetime.now()
  if time_value>=time_now:
    return True
  else:
     return False  
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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }]
  data1=[]
  venues=[]
  num_upcoming_shows=0
  venue_loop=Venue.query.all()
  city_state=set()
  for venue_item in venue_loop:
    city_state.add((venue_item.city,venue_item.state))
  for city_state_item in city_state:
    data1.append({
       "city":city_state_item[0],
        "state":city_state_item[1],
        "venues":[]
    })
  for venue_item in venue_loop:  
    venues_in_city_state=db.session.query(Venue).filter(venue_item.id==Venue.id).filter(venue_item.name==Venue.name).all()
    show_results=db.session.query(Shows).filter(venue_item.id==Shows.venue_id).all()
    for venues_c_s_item in venues_in_city_state: 
      for show_item in show_results:
        value=show_item.start_time
        if(compare_date(value)==True):
          num_upcoming_shows+=1
      for places in data1:
        if(venues_c_s_item.city==places['city'] and venues_c_s_item.state== places['state']):  
          places['venues'].append({
            "id":venues_c_s_item.id,
            "name":venues_c_s_item.name,
            "num_upcoming_shows":num_upcoming_shows
          }) 
  return render_template('pages/venues.html', areas=data1)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  search_term=request.form.get('search_term')
  venue_results=Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  data1=[]
  for venue_result in venue_results:
    show_results=db.session.query(Shows).filter(venue_result.id==Shows.venue_id).all()
    num_upcoming_shows=0
    for show_result in show_results:
      value=show_result.start_time
      if(compare_date(value)==True):
         num_upcoming_shows+=1
    data1.append({
      "id": venue_result.id,
      "name": venue_result.name,
      "num_upcoming_shows": num_upcoming_shows
    })
  
  response1={
    "count": len(venue_results),
    "data" : data1
  }
  return render_template('pages/search_venues.html', results=response1, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data1={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows": [{
      "artist_id": 4,
      "artist_name": "Guns N Petals",
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "address": "335 Delancey Street",
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "address": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    "past_shows": [{
      "artist_id": 5,
      "artist_name": "Matt Quevedo",
      "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [{
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 1,
    "upcoming_shows_count": 1,
  }

  venue_item=Venue.query.get(venue_id)
  data1=[]
  upcoming_shows=[]
  past_shows=[]
  past_shows_count=0
  upcoming_shows_count=0
  show_loop=db.session.query(Shows).filter(venue_item.id==Shows.venue_id).all()
  for show_item in show_loop:
      artist_item=Artist.query.get(show_item.artist_id)
      value=show_item.start_time
      if (compare_date(value)==True):
        upcoming_shows_count+=1
        upcoming_shows.append({
         "artist_id": artist_item.id,
         "artist_name":artist_item.name,
         "artist_image_link":artist_item.image_link,
         "start_time":show_item.start_time.strftime("%Y-%m-%d %H:%M:%S")
        })
      else:
        past_shows_count+=1
        past_shows.append({
        "artist_id": artist_item.id,
        "artist_name":artist_item.name,
        "artist_image_link":artist_item.image_link,
        "start_time":show_item.start_time.strftime("%Y-%m-%d %H:%M:%S")
        })
  data1={
      "id":venue_item.id,
      "name":venue_item.name,
      "genres":venue_item.genres,
      "address":venue_item.address,
      "city": venue_item.city,
      "state": venue_item.state,
      "phone": venue_item.phone,
      "website": venue_item.website,
      "facebook_link": venue_item.facebook_link,
      "seeking_talent":venue_item.seeking_talent,
      "image_link": venue_item.image_link,
      "past_shows":past_shows,
      "upcoming_shows":upcoming_shows,
      "past_shows_count":past_shows_count,
      "upcoming_shows_count":upcoming_shows_count
    }
  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data1)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  data1={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows": [{
      "artist_id": 4,
      "artist_name": "Guns N Petals",
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  # TODO: modify data to be the data object returned from db insertion
  error=False
  try:
    if request.form.get("seeking_talent")=="y":
      seektalent=True
    else:
      seektalent=False
    venue = Venue(
      name=request.form.get("name"),
      city=request.form.get("city"),
      state=request.form.get("state"),
      address=request.form.get("address"),
      phone=request.form.get("phone"),
      image_link=request.form.get("image_link"),
      facebook_link=request.form.get("facebook_link"),
      genres=','.join(request.form.getlist("genres")),
      website=request.form.get("website"),
      seeking_talent=seektalent,
      seeking_description=request.form.get("seeking_description")
    )
    db.session.add(venue)
    db.session.commit()          
  except:
        error=True
        db.session.rollback()
        print(sys.exc_info())
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' +' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
        db.session.close()  
  if not error:
         # on successful db insert, flash success
       flash('Venue ' + request.form.get("name") + ' was successfully listed!')
 
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error=False
  try:
   venue=Venue.query.get(venue_id)
   db.session.delete(venue)
   db.session.commit()
  except:
   error=True
   db.session.rollback()
   flash('An error occurred.Venue couldnot be deleted')
  finally:
    db.session.close()
  if not error:
     flash('Venue was successfully deleted!')
     
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=[{
    "id": 4,
    "name": "Guns N Petals",
  }, {
    "id": 5,
    "name": "Matt Quevedo",
  }, {
    "id": 6,
    "name": "The Wild Sax Band",
  }]
  data1=[]
  artist_loop=Artist.query.all()
  for artist_item in artist_loop:
    data1.append({
      "id": artist_item.id,
      "name": artist_item.name
    })

  return render_template('pages/artists.html', artists=data1)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }

  search_term=request.form.get('search_term')
  artist_results=Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  data1=[]
  for artist_result in artist_results:
    show_results=db.session.query(Shows).filter(artist_result.id==Shows.artist_id).all()
    num_upcoming_shows=0
    for show_result in show_results:
      value=show_result.start_time
      if(compare_date(value)==True):
         num_upcoming_shows+=1
    data1.append({
      "id": artist_result.id,
      "name": artist_result.name,
      "num_upcoming_shows": num_upcoming_shows
    })
  response1={
    "count": len(artist_results),
    "data" : data1
  }
  return render_template('pages/search_artists.html', results=response1, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data1={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "past_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  }
  artist_item=Artist.query.get(artist_id)
  data1=[]
  upcoming_shows=[]
  past_shows=[]
  past_shows_count=0
  upcoming_shows_count=0
  show_loop=db.session.query(Shows).filter(artist_item.id==Shows.artist_id).all()
  for show_item in show_loop:
      venue_item=Venue.query.get(show_item.venue_id)
      value=show_item.start_time
      if (compare_date(value)==True):
        upcoming_shows_count+=1
        upcoming_shows.append({
         "venue_id": venue_item.id,
         "venue_name":venue_item.name,
         "venue_image_link":venue_item.image_link,
         "start_time":show_item.start_time.strftime("%Y-%m-%d %H:%M:%S")
        })
      else:
        past_shows_count+=1
        past_shows.append({
        "venue_id": venue_item.id,
        "venue_name":venue_item.name,
        "venue_image_link":venue_item.image_link,
        "start_time":show_item.start_time.strftime("%Y-%m-%d %H:%M:%S")
        })
  data1={
      "id":artist_item.id,
      "name":artist_item.name,
      "genres":artist_item.genres,
      "city": artist_item.city,
      "state": artist_item.state,
      "phone": artist_item.phone,
      "facebook_link": artist_item.facebook_link,
      "seeking_venue":artist_item.seeking_venue,
      "image_link": artist_item.image_link,
      "past_shows":past_shows,
      "upcoming_shows":upcoming_shows,
      "past_shows_count":past_shows_count,
      "upcoming_shows_count":upcoming_shows_count
    }
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data1)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  artist=Artist.query.get(artist_id)
  form=ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist=Artist.query.get(artist_id)
  error=False
  try:
    artist.name=request.form.get("name")
    artist.city=request.form.get("city")
    artist.state=request.form.get("state")
    artist.phone=request.form.get("phone")
    artist.facebook_link=request.form.get("facebook_link")
    artist.genres=','.join(request.form.getlist("genres"))
    artist.website=request.form.get("website")
    artist.image_link=request.form.get("image_link")
    if request.form.get("seeking_venue")=='y':
       artist.seeking_venue=True   
    else:
       artist.seeking_venue=False
    artist.seeking_description=request.form.get("seeking_description")   
    db.session.commit()          
  except:
        error=True
        db.session.rollback()
        print(sys.exc_info())
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Artist ' +' could not be updated.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
        db.session.close()  
  if not error:
         # on successful db insert, flash success
       flash('Artist ' + request.form.get("name") + ' was successfully updated!')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }

  # TODO: populate form with values from venue with ID <venue_id>
  venue=Venue.query.get(venue_id)
  form=VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  venue=Venue.query.get(venue_id)
  error=False
  try:
    venue.name=request.form.get("name")
    venue.city=request.form.get("city")
    venue.state=request.form.get("state")
    venue.address=request.form.get("address")
    venue.phone=request.form.get("phone")
    venue.facebook_link=request.form.get("facebook_link")
    venue.genres=','.join(request.form.getlist("genres"))
    venue.website=request.form.get("website")
    venue.image_link=request.form.get("image_link")
    if request.form.get("seeking_talent")=='y':
       venue.seeking_talent=True
       
    else:
       venue.seeking_talent=False
    venue.seeking_description=request.form.get("seeking_description")   
    db.session.commit()          
  except:
        error=True
        db.session.rollback()
        print(sys.exc_info())
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' +' could not be updated.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
        db.session.close()  
  if not error:
         # on successful db insert, flash success
       flash('Venue ' + request.form.get("name") + ' was successfully updated!')
 
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error=False
  if request.form.get("seeking_venue")=="y":
    seekvenue=True
  else:
    seekvenue=False
  try:
    artist = Artist(
        name=request.form.get("name"),
        city=request.form.get("city"),
        state=request.form.get("state"),
        phone=request.form.get("phone"),
        image_link=request.form.get("image_link"),
        facebook_link=request.form.get("facebook_link"),
        genres=','.join(request.form.getlist("genres")),
        website=request.form.get("website"),
        seeking_venue=seekvenue,
        seeking_description=request.form.get("seeking_description")
      )
    db.session.add(artist)
    db.session.commit()          
  except:
          error=True
          db.session.rollback()
          print(sys.exc_info())
          # TODO: on unsuccessful db insert, flash an error instead.
          flash('An error occurred. Artist ' +' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
          db.session.close()  
  if not error:
          # on successful db insert, flash success
        flash('Artist ' + request.form.get("name") + ' was successfully listed!')

  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  data1=[]
  show_loop=Shows.query.all()
  for show_item in show_loop:
    venue_loop=db.session.query(Venue).filter(show_item.venue_id==Venue.id).all()
    artist_loop=db.session.query(Artist).filter(show_item.artist_id==Artist.id).all()
    for venue_item in venue_loop:
        venue_name=venue_item.name
    for artist_item in artist_loop:
        artist_name= artist_item.name
        artist_image_link= artist_item.image_link
    data1.append({
      "venue_name":venue_name,
      "venue_id": show_item.venue_id,
      "artist_id": show_item.artist_id,
      "artist_name":artist_name,
      "artist_image_link":artist_image_link,
      "start_time": show_item.start_time.strftime("%Y-%m-%d %H:%M:%S")
    })
  return render_template('pages/shows.html', shows=data1)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error=False
  try:
    show=Shows(
      start_time=format_datetime(request.form.get("start_time"), format='full'),
      artist_id=request.form.get("artist_id"),
      venue_id=request.form.get("venue_id")
    )
    db.session.add(show)
    db.session.commit()
  except:
    error=True
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
  # on successful db insert, flash success
  finally:
    db.session.close()
  if not error:
    flash('Show was successfully listed!')
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
