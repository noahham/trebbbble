# link-to-music

A web application that allows users to extract the music from short-form video content such as TikToks, Instagram Reels, and YouTube Shorts by simply providing a video URL. The app processes the video, identifies the background music, and provides the track details.

## Features

- Accepts TikTok, Instagram Reels, and YouTube Shorts links.
- Automatically downloads the video audio.
- Identifies the song using ACRCloud.

## How It Works

1. User submits a video URL.
2. The app downloads the video and extracts its audio.
3. The audio is processed through ACRCloud to identify the music.
4. If the song is found, its details are fetched from Spotify.
5. The app displays the song name, artist, and a Spotify link.

## Requirements

1. `keys.txt` which includes both ACRCloud and Spotify API keys (formatted as seen in `requirements.txt`).
3. All other dependencies in `requirements.txt`.
