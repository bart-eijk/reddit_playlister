Reddit Playlister
=================

Uses Reddit API and Spotify API to translate hottest of posts of subreddits to Spotify playlists

Requirements
--------------
* Spotify Premium + Application Key (https://devaccount.spotify.com/my-account/keys/)
* libspotify (https://developer.spotify.com/technologies/libspotify/)
* pyspotify 2.x (https://github.com/mopidy/pyspotify)
* requests (http://docs.python-requests.org/en/latest/)
* numpy (http://www.numpy.org)
* FuzzyWuzzy (https://github.com/seatgeek/fuzzywuzzy)

How to use
--------------
1. Clone the repository.
2. Get your Application Key from Spotify and place the `spotify_appkey.key` in the same directory as the script.
3. Use the -s argument to specify a subreddit (default is /r/Music) and run the script to generate a playlist from the 100 latest hot submissions.

License
--------------
This project is licensed under GPL v3.