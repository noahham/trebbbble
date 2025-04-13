# Trebbbble

A web application that allows users to extract the music from short-form video content such as TikToks, Instagram Reels, and YouTube Shorts by simply providing a video URL. The app processes the video, identifies the background music, and provides the track details.

## How It Works

1. User submits a URL of a TikTok, YouTube Short, or Instagram Reel.
2. The site downloads the video and extracts its audio.
3. The audio is processed through ACRCloud to identify the music.
4. If the song is found, its details are fetched from Spotify, YouTube Music, and Apple Music.
5. The site displays the song's name, artist, and its various music streaming links.

## Disclaimer
This is literally only the frontend website, the actual logic (and the stuff you wanna copy if you want to do a similar thing) is in my `trebbbble-backend` repository.
