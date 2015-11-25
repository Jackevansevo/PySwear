"""
Flask routing file to generate static web pages. Pulls data from the Pyswear
database and uses Chartkick to make pretty info graphics
"""

import sqlite3
import chartkick
from flask import (
    Flask,
    Blueprint,
    g,
    render_template,
)
from flask_sslify import SSLify

# configuration
DATABASE = 'pyswear.db'
DEBUG = False
SECRET_KEY = 'my_precious'
USERNAME = 'admin'
PASSWORD = 'admin'

# create an initialize app
APP = Flask(__name__)
sslify = SSLify(APP)
APP.config.from_object(__name__)

# Create a chartkick blueprint (see documentation for details)
CK = Blueprint('ck_page', __name__, static_folder=chartkick.js(), static_url_path='static')
APP.register_blueprint(CK, url_prefix='/ck')
APP.jinja_env.add_extension("chartkick.ext.charts")


@APP.route('/')
def show_index_page():
    """Shows the about page"""
    return render_template('index.html')


@APP.route('/artist-index')
def show_artist_index():
    """Displays an index of all the artists in the database"""
    artists = query_db('select * from artists order by artist_swear_count desc')
    graph1 = {}
    graph2 = {}
    graph3 = {}
    total_swear_count = 0
    for artist in artists:
        total_swear_count += artist['artist_swear_count']
        graph1[artist['artist_name']] = artist['artist_swear_count']
        graph2[artist['artist_name']] = artist['avg_swear_per_track']

    for artist in artists:
        artist_percentage = round(artist['artist_swear_count']/total_swear_count, 2)
        graph3[artist['artist_name']] = artist_percentage

    return render_template('artist_index.html', artists=artists,
                           graph1=graph1, graph2=graph2, graph3=graph3)


@APP.route('/artist/<artist_slug>')
def show_artist_page(artist_slug):
    """Creates an individual page for each artist"""
    artist = query_db('select * from artists where artist_slug = ?',
                      [artist_slug], one=True)

    albums = query_db('select * from albums where album_artist = ? order by album_swear_count desc', [artist['artist_id']])

    dated_albums = query_db('select * from albums where album_artist = ? order by album_release_year', [artist['artist_id']])

    swear_words_over_time_graph = {}
    column_chart = {}
    pie_chart = {}
    for album in albums:
        column_chart[album['album_name']] = album['album_swear_count']
        pie_chart[album['album_name']] = round(album['album_swear_count'] / artist['artist_swear_count'], 2)

    for album in dated_albums:
        swear_words_over_time_graph[album['album_release_year']] = album['album_swear_count']
    return render_template('artist_page.html', artist=artist, albums=albums,
                           column_chart=column_chart, pie_chart=pie_chart,
                           swear_words_over_time_graph=swear_words_over_time_graph)


@APP.route('/artist/<artist_slug>/<album_slug>')
def show_album_page(artist_slug, album_slug):
    """Creates an individual page for each album"""
    artist = query_db('select * from artists where artist_slug = ?',
                      [artist_slug], one=True)

    # [FIXME] This is bad some albums have the same title
    album = query_db('select * from albums where album_slug = ?', [album_slug], one=True)

    tracks = query_db('select * from tracks where track_album = ?', [album['album_id']])

    bar_chart = {}
    pie_chart = {}
    for track in tracks:
        bar_chart[track['track_name']] = track['track_swear_count']
        pie_chart[track['track_name']] = round(track['track_swear_count'] / album['album_swear_count'], 2)

    return render_template('album_page.html', album=album, artist=artist, tracks=tracks, bar_chart=bar_chart, pie_chart=pie_chart)


@APP.route('/artist/<artist_slug>/<album_slug>/<track_slug>')
def show_track_page(artist_slug, album_slug, track_slug):
    """Creates an individual page for each track"""
    artist = query_db('select * from artists where artist_slug = ?', [artist_slug], one=True)

    # [TODO] FIXME
    album = query_db('select * from albums where album_slug = ?', [album_slug], one=True)

    track = query_db('select * from tracks where track_slug = ?', [track_slug], one=True)

    # [TODO] Prevent repeated words
    words = query_db('select * from words where word_track = ? order by count desc', [track['track_id']])

    bar_chart = {}
    pie_chart = {}
    for word in words:
        bar_chart[word['word']] = word['count']
        pie_chart[word['word']] = round(word['count'] / track['track_swear_count'], 2)
    return render_template('track_page.html', words=words, track=track,
                           artist=artist, album=album, bar_chart=bar_chart,
                           pie_chart=pie_chart)


@APP.errorhandler(404)
def page_not_found(error):
    """Route for error 404 page not found page"""
    return render_template('page_not_found.html'), 404


@APP.before_request
def before_request():
    """Opens a connection to the database"""
    g.db = connect_db()


@APP.teardown_request
def teardown_request(exception):
    """Closes connection to the database"""
    database = getattr(g, 'db', None)
    if database is not None:
        database.close()


def query_db(query, args=(), one=False):
    """Quickly query the database"""
    cur = g.db.execute(query, args)
    row_value = [dict((cur.description[idx][0], value) for idx, value in
                      enumerate(row)) for row in cur.fetchall()]
    return (row_value[0] if row_value else None) if one else row_value


def connect_db():
    """Connects to the database"""
    conn = sqlite3.connect('pyswear.db')
    conn.row_factory = sqlite3.Row
    return conn

if __name__ == '__main__':
    APP.run()
