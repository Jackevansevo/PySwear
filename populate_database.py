"""
Loops through the ARTISTS text file line by line, creating a separate Thread
for each ARTISTS then beings scraping the web for that artists discography
"""

from database import DataBaseConnection
from scrape_web import WebScraper
from multiprocessing.pool import Pool
import sys


def create_scraper_instance(artist_name):
    """Creates instances of web scraper and returns the result"""
    verbose_flag = False
    if len(sys.argv) > 1 and (sys.argv[1]) == "-v":
        verbose_flag = True
    scraper = WebScraper(artist_name, verbose_flag)
    scraper.run()
    print("Finished Scraping: " + artist_name)
    return scraper.scrape_results


def add_artists(results):
    """Loops through the results and adds artists to the database"""
    for artist_result in results:
        print("Adding: " + artist_result.get('artist_info')[0])
        # Add the individual artist to the database
        artist_info = artist_result.get('artist_info')

        query = "insert into artists(artist_name, artist_slug) values(?, ?)"
        CONN.run_query(query, artist_info)

        # Get the artists unique ID
        artist_id = CONN.get_artist_id(artist_info[0])

        # Loop through the artists albums and add them to the database
        add_albums(artist_result, artist_id)


def add_albums(artist_result, artist_id):
    """Loops through the results and adds albums to the database"""
    for album in artist_result.get('albums'):
        album_info = album.get('album_info')

        # Add the album information to the database
        query = """
        insert into albums(album_name, album_slug, album_release_year,
        album_artist) values(?, ?, ?, ?)
        """
        CONN.run_query(query, album_info + artist_id)

        # Get the albums unique ID
        album_id = CONN.get_album_id(album_info[0])

        # Loop through each track on the album and add to the database
        add_tracks(album, album_id)


def add_tracks(album, album_id):
    """Loops through the results and adds tracks to the database"""
    for track in album.get('tracks'):
        track_info = track.get('track_info')

        # Add the track information to the database
        query = """
        insert into tracks(track_name, track_slug, track_album) values(?, ?, ?)
        """
        CONN.run_query(query, track_info + album_id)

        # Get the tracks unique ID
        track_id = CONN.get_track_id(track_info[0])

        if len(track.get('swear_count').items()):
            for word, count in track.get('swear_count').items():
                CONN.add_word((word, count), track_id)


def tally_swear_count(artist):
    """Works out number of swear words for each song, album and artist"""
    artist_swear_count = 0
    qry = 'select * from albums where album_artist=?'
    track_count = 0
    album_count = 0
    for album in CONN.query_db(qry, [artist['artist_id']]):
        album_count += 1
        album_swear_count = 0
        qry = 'select * from tracks where track_album=?'

        for track in CONN.query_db(qry, [album['album_id']]):
            track_count += 1
            track_swear_count = 0
            qry = 'select * from words where word_track=? '

            for word in CONN.query_db(qry, [track['track_id']]):
                track_swear_count += word['count']

            qry = 'update tracks set track_swear_count=? where track_id=?'
            CONN.run_query(qry, (track_swear_count, track['track_id']))
            album_swear_count += track_swear_count

        qry = 'update albums set album_swear_count=? where album_id=?'
        CONN.run_query(qry, (album_swear_count, album['album_id']))
        artist_swear_count += album_swear_count

    qry = 'update artists set artist_swear_count=? where artist_id=?'
    CONN.run_query(qry, (artist_swear_count, artist['artist_id']))

    # Calculate the the average swear count per track/ablum
    avg_track = round(artist_swear_count/track_count)
    avg_album = round(artist_swear_count/album_count)
    qry = """update artists set avg_swear_per_track = ?, avg_swear_per_album =
    ? where artist_name = ?"""
    CONN.run_query(qry, (avg_track, avg_album, artist['artist_name']))


if __name__ == '__main__':
    # Make a connection to the database
    CONN = DataBaseConnection('pyswear.db')
    CONN.run_script('schema.sql')

    ARTISTS = tuple([line.rstrip('\n') for line in open('artists.txt')])
    POOL = Pool(len(ARTISTS))
    # Creates scraper instances in separate thread for each artist
    SCRAPE_RESULTS = POOL.map(create_scraper_instance, ARTISTS)

    print("Adding artists")
    add_artists(SCRAPE_RESULTS)

    # Tally the swear count for each artist
    for artist_result in CONN.query_db('select * from artists'):
        tally_swear_count(artist_result)
