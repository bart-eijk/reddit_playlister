Reddit Playlister
=================

Reddit Playlister uses the Reddit API to get the 100 latest hot submissions of any subreddit, filter out the songs, and turn it into a Spotify playlist. Currently, the script provides limited functionality, future updates should include custom playlist names and improved song filtering.

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

Example
--------------
`python main.py -s Rock` will generate a Spotify playlist with the name "/r/Rock 1-jan-2015" (if run on the first of January).

License
--------------
This project is licensed under GPL v3.