import requests
import json
import re
import argparse
from contextlib import contextmanager
from spotify_api import Spotify
from datetime import datetime
import getpass


# wrapper for managing logged in sessions
@contextmanager
def logged_in_session(s):

    s.login()
    yield s
    s.logout()


def filter(subm):
    """
    Returns whether a Reddit submission is a song stream.
    """
    return (subm['data']['domain'].endswith("youtube.com") or
            subm['data']['domain'].endswith("youtu.be") or
            subm['data']['link_flair_text'] == "Stream")


def get_submissions(subreddit, limit=100):
    """
    Get n latest hot submissions from subreddit using Reddit API.
    """
    user_agent = {'User-Agent': 'Reddit Playlister'}
    parameters = {'limit': limit}
    r = requests.get("http://www.reddit.com/r/{0}/hot/.json".format(subreddit),
                     params=parameters,
                     headers=user_agent)
    return r.json()


def filter_songs(submissions):
    """
    Checks if a Reddit submission is a song and returns the song artist
    and title.
    """
    for subm in submissions['data']['children']:
        if filter(subm):
            raw = subm['data']['title']

            # remove [genre] from string
            if "[" in raw:
                raw = raw[0:raw.find("[")-1]

            # remove anything in parantheses from string
            if "(" in raw:
                raw = raw[0:raw.find("(")-1]

            # get artist and title
            song_info = re.split(r'\s*-+\s*', raw)

            if len(song_info) > 1:
                yield song_info


def main():
    description = ("Generates a Spotify playlist from the submissions of any "
                   "sub-reddit. If no subreddit is specified, /r/Music is "
                   "used. Currently, the playlist to be used needs to be "
                   "created by the user beforehand.")
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-s', '--subreddit',
                        default='Music',
                        help=("Subreddit to use as source (standard is "
                              "/r/Music if non is given)"))
    args = parser.parse_args()

    # parse the subreddit from the user input, remove /r/ and closing slash
    _subr = args.subreddit.split("/")
    if _subr[-1] == '':
        subreddit = _subr[-2]
    else:
        subreddit = _subr[-1]

    # get user credentials
    username = ""
    password = ""
    while username == "":
        username = raw_input("Username: ")
    while password == "":
        password = getpass.getpass("Password: ")

    # initialize Spotify API session
    s = Spotify(username, password)

    print "Querying Reddit for submissions..."
    submissions = get_submissions(subreddit)
    print "  Retrieved {0} submissions from /r/{1}.".format(
        len(submissions['data']['children']), subreddit)
    songs = list(filter_songs(submissions))
    print "  {0} song submissions found!".format(len(songs))

    with logged_in_session(s):

        # create the playlist ("/r/{subreddit} {current_date}") and load it
        current_date = datetime.now().strftime('%d-%b-%Y').lower()
        playlist_name = "/r/{0} {1}".format(subreddit, current_date)
        s.create_playlist(playlist_name)
        s.get_playlist(playlist_name)

        tracks = []
        for song in songs:
            spotify_track = s.find_track(song[0], song[1])
            if spotify_track:
                print ("  Matched submission \"{0} - {1}\" "
                       "to Spotify track \"{2} - {3}\"").format(
                    s.normalize_string(song[0]),
                    s.normalize_string(song[1]),
                    s.normalize_string(spotify_track.artists[0].name),
                    s.normalize_string(spotify_track.name))
                tracks.append(spotify_track)
            else:
                print "  Track not found! \"{0} - {1}\"".format(
                    s.normalize_string(song[0]),
                    s.normalize_string(song[1]))
        print "Found {0}/{1} tracks!".format(len(tracks), len(songs))

        for t in tracks:
            s.add_track(t)


if __name__ == '__main__':
    main()
