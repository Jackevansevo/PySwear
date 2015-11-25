"""Simple class allowing programs to interface with an sqlite3 database"""

import sqlite3


class DataBaseConnection(object):
    """Creates a connection to the database"""
    def __init__(self, db):
        """Default constructor for new database connections"""
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()

    def add_word(self, data, word_track):
        """Adds a word and it's occurrence frequency to the database"""
        query = "insert into words(word, count, word_track) values(?, ?, ?)"
        self.run_query(query, data + word_track)

    def get_artist_id(self, artist_name):
        """Returns the artist_id as a tuple fr a given artist name"""
        query = "select artist_id from artists where artist_name=?"
        try:
            self.cur.execute(query, (artist_name,))
            return self.cur.fetchone()
        except sqlite3.Error as error:
            print("Artist: " + artist_name + " not found in database: " +
                  error.args[0])

    def get_album_id(self, album_name):
        """Returns the album_id in a tuple for a given album name"""
        query = "select album_id from albums where album_name=?"
        try:
            self.cur.execute(query, (album_name,))
            return self.cur.fetchone()
        except sqlite3.Error as error:
            print("Album: " + album_name + " not found in database: " +
                  error.args[0])

    def get_track_id(self, track_name):
        """Returns the track_id in a tuple for a given track name"""
        query = "select track_id from tracks where track_name=?"
        try:
            self.cur.execute(query, (track_name,))
            return self.cur.fetchone()
        except sqlite3.Error as error:
            print("Track: " + track_name + " not found in database: " +
                  error.args[0])

    def run_query(self, query, data):
        """Queries the DB, running the query argument against data argument"""
        try:
            self.cur.execute(query, data)
            self.conn.commit()
        except (sqlite3.Error) as error:
            print("\nSqlite3 Database Error:", query, data, error.args[0])
        except (TypeError, ValueError, UnboundLocalError) as error:
            print("\nAn error occurred: " + error.args[0])
        except Error as error:
            print("\nAn Unexpected Error Occurred" + error.args[0])

    def query_db(self, query, args=(), one=False):
        """If successful returns sqlite3 row wrapped in a dictionary"""
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()
        self.cur.execute(query, args)
        row_val = self.cur.fetchall()
        return (row_val[0] if row_val else None) if one else row_val

    def get_results(self, query):
        """Get a list of results from the database"""
        try:
            self.cur.execute(query)
            return self.cur.fetchall()
        except sqlite3.Error as error:
            print(error.args[0])

    def run_script(self, script):
        """Initialize database with sql schema file"""
        script_file = open(script, 'r')
        script = script_file.read()
        script_file.close()
        try:
            self.cur.executescript(script)
            self.conn.commit()
        except sqlite3.Error as error:
            print("An error occurred when running script: " + str(script) +
                  error.args[0])

    def close_connection(self):
        """Closes the connection to the database"""
        self.conn.commit()
        self.conn.close()

    def __del__(self):
        """Tells the current thread to close it's connection to the db"""
