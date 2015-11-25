--Wipe any existing stuff in database, inefficient I know
--but makes it easier for testing purposes
drop table if exists artists;
drop table if exists albums;
drop table if exists tracks;
drop table if exists words;

create table artists (
    artist_id integer primary key autoincrement,
    artist_name text,
    artist_slug text,
    artist_swear_count integer,
    avg_swear_per_album integer,
    avg_swear_per_track integer
);

create table albums (
    album_id integer primary key autoincrement,
    album_name text,
    album_slug text,
    album_release_year text,
    album_swear_count integer,
    album_artist integer,
    FOREIGN KEY(album_artist) REFERENCES artists(artist_id)
);

create table tracks (
    track_id integer primary key autoincrement,
    track_name text,
    track_slug text,
    track_swear_count integer,
    track_album integer,
    FOREIGN KEY(track_album) REFERENCES albums(album_id)
);

create table words (
    word_id integer primary key autoincrement,
    word text,
    count integer default 0,
    word_track integer,
    FOREIGN KEY(word_track) REFERENCES albums(track_id)
);
