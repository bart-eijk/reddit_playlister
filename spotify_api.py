import spotify
import threading
import unicodedata
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import numpy as np


class Spotify():
    def __init__(self, user, passw):
        self.username = user
        self.password = passw
        self.playlist = None

        config = spotify.Config()
        config.user_agent = 'Reddit Playlister'

        self.session = spotify.Session(config)

    def filter_track(self, tracks):
        """
        Gets Track from nested Sequence-object or list
        """
        while type(tracks) != spotify.track.Track:
            tracks = tracks[0]
        return tracks

    def normalize_string(self, unicode_s):
        """
        Converts unicode to string (removing the accents from letters), removes
        double quotes and escapes HTML characters.
        """
        s = unicodedata.normalize('NFKD', unicode_s).encode('ASCII', 'ignore')
        return s.replace("&amp; ", "").replace('"', '')

    def login(self):
        """
        Logs current user in to Spotify. pyspotify's login() is asynchronous, 
        so it is recommended to use an EventLoop.
        """
        self.logged_in_event = threading.Event()
        loop = spotify.EventLoop(self.session)
        loop.start()
        self.session.on(
            spotify.SessionEvent.CONNECTION_STATE_UPDATED,
            self.connection_state_listener)

        self.session.login(self.username, self.password)
        self.logged_in_event.wait()

        if self.session.connection.state is spotify.ConnectionState.LOGGED_IN:
            print "User logged in:", self.session.user.display_name
        else:
            print ("Something went wrong! "
                   "Current state is: "), self.session.connection.state

    def logout(self):
        """
        Logs current user out of Spotify. Uses an EventLoop.
        """
        logged_out_event = threading.Event()

        def logged_out_listener(session):
            logged_out_event.set()

        self.session.on(spotify.SessionEvent.LOGGED_OUT, logged_out_listener)
        self.session.logout()

        if not logged_out_event.wait(10):
            raise RuntimeError('Logout timed out')
        else:
            print "{0} logged out.".format(self.username)

    def connection_state_listener(self, session):
        """
        Is used by login method.
        """
        if session.connection.state is spotify.ConnectionState.LOGGED_IN:
            self.logged_in_event.set()

    def find_track(self, artist_uni, title_uni, threshold=80):
        """
        Finds a track on Spotify, based on the artist and title of the
        track. Starts of a strict search with literal matching, after
        - when no match is found - switches to less stricter track
        matching.
        """
        artist = self.normalize_string(artist_uni)
        title = self.normalize_string(title_uni)

        # 1. use naive strict method with exact artist - title match
        query = "artist:{0} title:{1}".format(artist, title)
        search = self.session.search(query)
        search.load()
        tracks = search.tracks
        if search.track_total > 0:
            return self.filter_track(tracks)

        # 2. use less strict query without artist:- and title:-prefix
        query = artist + " " + title
        search = self.session.search(query)
        search.load()
        tracks = search.tracks
        if search.track_total > 0:
            return self.filter_track(tracks)

        # 3. find all tracks by artist and return largest partial match
        # above threshold
        query = "artist:{0}".format(artist)
        search = self.session.search(query)
        search.load()
        tracks = search.tracks
        if search.track_total > 0:
            matches = []
            for track in tracks:
                matches.append(fuzz.partial_ratio(title, track.name))
            best_match = np.argsort(matches)[-1]
            if matches[best_match] > threshold:
                return tracks[best_match]

    def get_playlist(self, playlist_name):
        """
        Loads a playlist into the current object.
        """
        container = self.session.playlist_container
        container.load()
        for p in container:
            if p.name == playlist_name.decode('utf-8'):
                self.playlist = p
        if self.playlist:
            print "Playlist {0} loaded!".format(playlist_name)
        else:
            raise Exception("Playlist {0} not found!".format(playlist_name))

    def create_playlist(self, name):
        """
        Creates a playlist.
        """
        container = self.session.playlist_container
        container.load()
        playlist = self.session.playlist_container.add_new_playlist(name)
        while playlist.has_pending_changes:
            self.session.process_events()
        print "Playlist succesfully created:", name

    def add_track(self, track):
        """
        Add a track to the currently loaded playlist. Make sure
        the playlist is loaded.
        """
        self.playlist.add_tracks(track)
        self.session.process_events()
        self.playlist.load()