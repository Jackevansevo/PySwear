"""
Web_Scraper object takes the name of an artist as an input then scrapes
genius.com to find all of that artsts discopgrahy, before saving all the data
to a sqlite3 database
"""

# [FIXME] Artists with names containing a '$' can't be found

from bs4 import BeautifulSoup
from calc_hook import get_hook
from collections import Counter, OrderedDict
import urllib.request
import re
import unidecode

# Add and remove keywords depending on what results we want to record
KEY_WORDS = ['bastard', 'bitch', 'cock', 'fag', 'fuck', 'fucked', 'fuckin',
             'hoes', 'marijuana', 'motherfucka', 'motherfucker', 'muthafucka',
             'muthafuckin', 'pussy', 'shit', 'weed']

# Make the keywords searchable by turning into a regex expression
KEY_WORDS_REGEX = ("|".join("\\b{0}\\b".format(w) for w in KEY_WORDS))

GREENFONT = "\033[1;32m{0}\033[00m"
REDFONT = "\033[1;31m{0}\033[00m"
BLUEFONT = "\033[1;36m{0}\033[00m"
ARTIST_URL_REGEX = r"http:\/\/genius.com\/artists\/"


class WebScraper:
    """Each instance scans www.genius.com for that artists discography"""

    def __init__(self, artist_name, verbose_flag):
        self.artist_name = artist_name
        self.verbose_flag = verbose_flag
        self.scrape_results = OrderedDict()
        self.artist_albums = []

    def run(self):
        """Starts the WebScraper"""
        self.get_artist_page_url()

    def get_artist_page_url(self):
        """Searches for page corresponding to artists name"""
        index_page_url = get_index_page_url(self.artist_name)
        soup = get_soup(index_page_url)
        if soup:
            artist_found = False
            # Scrape page for all http://genius.com/arists/ link
            for link in soup.findAll('a', href=re.compile(ARTIST_URL_REGEX)):
                # Look for the name inside each tag '<a href="url">ARTIST</a>'
                if re.search(self.artist_name, link.getText(), re.IGNORECASE):
                    artist_found = True
                    artist_info = (self.artist_name, slugify(self.artist_name))
                    self.scrape_results['artist_info'] = artist_info
                    print(GREENFONT.format("Found: " + self.artist_name))
                    # Scan the page for that artist
                    self.scan_artist_page(link['href'])
                    break
            if not artist_found:
                print(REDFONT.format("Artist not found: " + self.artist_name))

    def scan_artist_page(self, artist_page_url):
        """Scrapes the artist page for all albums by that artist"""
        soup = get_soup(artist_page_url)
        if soup:
            for link in soup.find_all('a', {'class': 'album_link'}):
                album_page_url = ("http://genius.com" + link.get('href'))
                self.scan_album_page(album_page_url)

    def scan_album_page(self, page_url):
        """Scrapes the album page for all the songs on that album"""
        # Create a dictionary for each album
        album_dict = OrderedDict()
        soup = get_soup(page_url)
        if soup:
            album_info = parse_album_info(soup)
            if album_info:
                album_dict['album_info'] = album_info
                if self.verbose_flag:
                    print(BLUEFONT.format(album_dict.get('album_info')[0]))
                # Create an empty array of tracks for the new album
                album_tracks = []
                # Scrape links for all the songs in the album
                for link in soup.find_all('a', {'class': 'song_name'}):
                    # Create an empty track dictionary to store track
                    # information
                    track_dict = OrderedDict()
                    track_name = str((link.find('span', class_='song_title').getText()))
                    if self.verbose_flag:
                        print(track_name)
                    lyrics = parse_track_lyrics(link.get('href'))
                    if lyrics is not None:
                        swear_count = get_swear_word_count(lyrics)
                        if track_name is not None:
                            track_dict['track_info'] = (track_name,
                                                        slugify(track_name))
                            track_dict['swear_count'] = swear_count
                        # Once completed add the track dictionary to our array
                        # of tracks
                        if track_dict is not None:
                            album_tracks.append(track_dict)
                album_dict['tracks'] = album_tracks
                self.artist_albums.append(album_dict)
                self.scrape_results['albums'] = self.artist_albums


def slugify(text):
    """Convert text to a unicode slug"""
    text = unidecode.unidecode(text).lower()
    return re.sub(r'\W+', '-', text)


def parse_album_info(soup):
    """Parses album info and returns data as a tuple"""
    release_year_span = (soup.h1.span.contents)
    if release_year_span:
        album_release_year = release_year_span[0].strip()
    else:
        album_release_year = "N/A"

    album_name = soup.h1.contents[0].strip()
    # Filter out some bogus album results
    if album_name.lower().endswith(('.jpg', 'version)', 'review', 'bonus')):
        return None
    album_slug = slugify(album_name)
    return(album_name, album_slug, album_release_year)


def get_swear_word_count(lyrics):
    """Returns a dictoinary of swear word frequency of inputted lyrics"""
    # Count how many swear words are in the entire song
    swear_count = Counter(w.lower() for w in re.findall(KEY_WORDS_REGEX, lyrics.lower()))
    # If a [Hook] tag appears in the song get it's contents then multiply it's
    # swear count by the number of times the tag repeats
    if len(re.findall(r"\n\[Hook\]\n.", lyrics)) > 0:
        hook_lyrics = get_hook(lyrics).lower()
        # Count all the swear words in the initial hook
        hook_swear_count = Counter(w.lower() for w in re.findall(KEY_WORDS_REGEX, hook_lyrics))
        # Get the rest of the standalone [Hook] tags which don't include
        # lyrics
        hook_tag_count = len(re.findall(r"\[Hook\]\n\s", lyrics))
        if hook_tag_count:
            for word, count in hook_swear_count.items():
                hook_swear_count[word] = count * hook_tag_count
            swear_count += hook_swear_count
    return swear_count


def parse_track_lyrics(track_page):
    """Scrapes the lyrics from the corresponding track page"""
    soup = get_soup(track_page)
    if soup:
        for lines in soup.find_all('div', {'class': 'lyrics'}):
            # count the numebr of swear words in just the text
            return lines.getText()


def get_index_page_url(name):
    """Return the url of the index page corresponding to an artist name"""
    index_url = "http://genius.com/artists-index/"
    # If the first letter is a number look at index '0'
    if re.search(r"\d", name[0]):
        return index_url + '0'
    else:
        return index_url + name[0]


def get_soup(url):
    """Returns the html from a page"""
    try:
        # It throws a bunch of errors if you don't add the following headers
        req = urllib.request.Request(url, headers={'User-Agent':
                                                   'Mozilla/5.0'})
        webpage = urllib.request.urlopen(req).read()
        # Using lxml because it's quicker
        return BeautifulSoup(webpage, "lxml")
    except urllib.error.HTTPError:
        return None
