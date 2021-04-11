#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from models import app, db, Venue, Artist, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

db.init_app(app)
moment = Moment(app)



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
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

  data = []
  cities = db.session.query(Venue).distinct(Venue.city).all()
  for result in cities:
    #print(result.city)
    venues = Venue.query.filter_by(city=result.city).all()
    data.append({'city': result.city, 'state': result.state, 'venues': list(venues)})

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():

  response = {}
  search_term = (request.form['search_term'])
  query_result = Venue.query.filter(Venue.name.ilike('%'+search_term+'%'))
  response['count'] = len(list(query_result))
  response['data'] = query_result

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id

  result_query_venue = Venue.query.filter_by(id=venue_id).all()[0]
  data = result_query_venue.__dict__
  q = db.session.query(Artist, Show).join(Artist.show).filter_by(venue_id=venue_id)
  qresult = q.all()
  total_past_shows = 0
  total_upc_shows = 0
  past_shows = []
  upcoming_shows = []
  for tup in qresult:
    if tup[1].start_time <= datetime.now():
      new_past_show = {}
      new_past_show["artist_id"] = tup[0].id
      new_past_show["artist_name"] = tup[0].name
      new_past_show["artist_image_link"] = tup[0].image_link
      new_past_show["start_time"] = str(tup[1].start_time)
      past_shows.append(new_past_show)
      total_past_shows += 1
    else:
      new_upc_show = {}
      new_upc_show["artist_id"] = tup[0].id
      new_upc_show["artist_name"] = tup[0].name
      new_upc_show["artist_image_link"] = tup[0].image_link
      new_upc_show["start_time"] = str(tup[1].start_time)
      upcoming_shows.append(new_upc_show)
      total_upc_shows += 1

  data['upcoming_shows'] = upcoming_shows
  data['past_shows'] = past_shows
  data['past_shows_count'] = total_past_shows
  data['upcoming_shows_count'] = total_upc_shows

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  #get values from form
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  phone = request.form.get('phone')
  genres = request.form.getlist('genres')
  facebook_link = request.form.get('facebook_link')
  image_link = request.form.get('image_link')
  website_link = request.form.get('website_link')
  if request.form.get('seeking_talent') == 'y':
    seeking_talent = True
  else:
    seeking_talent = False
  seeking_description = request.form.get('seeking_description')

  #create artist object with form values
  new_venue = Venue(name=name,
                  city=city,
                  state=state,
                  phone=phone,
                  genres=genres,
                  facebook_link=facebook_link,
                  image_link=image_link,
                  website_link=website_link,
                  seeking_talent=seeking_talent,
                  seeking_description=seeking_description
                  )

  #add obj to the session and commit to the db
  try:
    db.session.add(new_venue)
    db.session.commit()
  # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + new_venue.name + ' could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('The venue has been removed together with all of its shows.')
  except:
    flash('It was not possible to delete this Venue')
    db.session.rollback()
  finally:
    db.session.close()

  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  data=[]
  artists = Artist.query.all()
  for artist in artists:
    new_summary = {'id': artist.id, 'name': artist.name}
    data.append(new_summary)

  return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():

  response = {}
  search_term = (request.form['search_term'])
  query_result = Artist.query.filter(Artist.name.ilike('%'+search_term+'%'))
  response['count'] = len(list(query_result))
  response['data'] = query_result
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id

  result_query_artist = Artist.query.filter_by(id=artist_id).all()[0]
  data = result_query_artist.__dict__
  q = db.session.query(Venue, Show).join(Venue.show).filter_by(artist_id=artist_id)
  qresult = q.all()
  total_past_shows = 0
  total_upc_shows = 0
  past_shows = []
  upcoming_shows = []
  for tup in qresult:
    if tup[1].start_time <= datetime.now():
      new_past_show = {}
      new_past_show["venue_id"] = tup[0].id
      new_past_show["venue_name"] = tup[0].name
      new_past_show["venue_image_link"] = tup[0].image_link
      new_past_show["start_time"] = str(tup[1].start_time)
      past_shows.append(new_past_show)
      total_past_shows += 1
    else:
      new_upc_show = {}
      new_upc_show["venue_id"] = tup[0].id
      new_upc_show["venue_name"] = tup[0].name
      new_upc_show["venue_image_link"] = tup[0].image_link
      new_upc_show["start_time"] = str(tup[1].start_time)
      upcoming_shows.append(new_upc_show)
      total_upc_shows += 1

  data['upcoming_shows'] = upcoming_shows
  data['past_shows'] = past_shows
  data['past_shows_count'] = total_past_shows
  data['upcoming_shows_count'] = total_upc_shows
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  artist=Artist.query.filter_by(id=artist_id).all()[0]

  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  artist=Artist.query.filter_by(id=artist_id).all()[0]
  form = ArtistForm(request.form)
  try:
    form.populate_obj(artist)

    db.session.add(artist)
    db.session.commit()
    flash(f'Artist {form.name.data} was successfully edited!')
  except ValueError as e:
    db.session.rollback()
    flash(f'An error occurred in {form.name.data}. Error: {str(e)}')
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.filter_by(id=venue_id).all()[0]

  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  edit_venue = Venue.query.filter_by(id=venue_id).all()[0]
  form = VenueForm(request.form)
  try:
    form.populate_obj(edit_venue)
    db.session.add(edit_venue)
    db.session.commit()
    flash(f'Venue {form.name.data} was successfully edited!')
  except ValueError as e:
    db.session.rollback()
    flash(f'An error occurred in {form.name.data}. Error: {str(e)}')
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  #get values from form
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  phone = request.form.get('phone')
  genres = request.form.getlist('genres')
  facebook_link = request.form.get('facebook_link')
  image_link = request.form.get('image_link')
  website_link = request.form.get('website_link')
  if request.form.get('seeking_venue') == 'y':
    seeking_venue = True
  else:
    seeking_venue = False
  seeking_description = request.form.get('seeking_description')


  #create artist object with form values
  artist = Artist(name=name,
                  city=city,
                  state=state,
                  phone=phone,
                  genres=genres,
                  facebook_link=facebook_link,
                  image_link=image_link,
                  website_link=website_link,
                  seeking_venue=seeking_venue,
                  seeking_description=seeking_description
                  )

  #add obj to the session and commit to the db
  try:
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + Artist.name + ' could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  data = []

  all_shows_join_query = db.session.query(Venue, Artist, Show).join(Venue).join(Artist)
  join_result = all_shows_join_query.all()


  for result in join_result:
    a_show = {}

    a_show["venue_id"] = result[0].id
    a_show["venue_name"] = result[0].name
    a_show["artist_id"] = result[1].id
    a_show["artist_name"] = result[1].name
    a_show["artist_image_link"] = result[1].image_link
    a_show["start_time"] = str(result[2].start_time)

    data.append(a_show)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form

  # get values from form
  artist_id = request.form.get('artist_id')
  venue_id = request.form.get('venue_id')
  start_time = request.form.get('start_time')

  # create artist object with form values
  new_show = Show(artist_id=artist_id,
                  venue_id=venue_id,
                  start_time=start_time,
                  )

  # add obj to the session and commit to the db
  try:
    db.session.add(new_show)
    db.session.commit()
  # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()
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
    db.init_app(app)
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
