import os
import time
import hmac
import hashlib
import base64
import requests
import spotipy
import urllib.parse
import yt_dlp
import ffmpeg
from spotipy.oauth2 import SpotifyClientCredentials

def load_api_keys(file_path : str) -> dict:
    """
    Reads API keys from a text file and returns them as a dictionary.

    Args:
        file_path (str): Path to the file containing the API keys.

    Returns:
        dict: A dictionary containing the API keys.
    """

    with open(file_path, "r") as f:
        keys = [line.strip() for line in f.readlines()]

    if len(keys) != 4:
        raise ValueError(
            "Invalid key file format. Ensure 4 lines: ACRCloud Client Key, ACRCloud Secret Key, Spotify Client Key, Spotify Secret Key.")

    return {
        "ACR_ACCESS_KEY": keys[0],
        "ACR_ACCESS_SECRET": keys[1],
        "SPOTIFY_CLIENT_ID": keys[2],
        "SPOTIFY_CLIENT_SECRET": keys[3]
    }

def download_video(url : str) -> None:
    """
    Scrapes video from either Reels, YT Shorts, or TikTok and writes to working directory.

    Args:
        url (str): URL to video from Reels, YT Shorts, or TikTok.
    """

    try:
        if "youtube.com" in url or "youtu.be" in url:
            if "shorts" not in url: # YouTube Shorts only
                print("Not a YouTube Shorts link.")
                return

        # yt-dlp options
        ydl_opts = {
            "outtmpl": "temp.mp4",  # Always save as temp.mp4
            "format": "mp4",        # TODO: Can this just do wav?
            "quiet": True,        # Supress logs
            "noprogress": True,    # Hide progress bar
            "overwrites": True    # This makes sure the file gets overwritten
        }

        print(f"Downloading video...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        print("Download successful.")

    except Exception as e:
        print(f"An error occurred: {e}")

def mp4_to_wav(input_file="temp.mp4", output_file="temp.wav") -> None:
    """
    Converts mp4 to wav file.

    Args:
        input_file (str): Path to the mp4 file.
        output_file (str): Path to the wav file.
    """

    try:
        ffmpeg.input(input_file).output(output_file).run()
        print(f"Successfully converted to WAV.")
        os.remove("temp.mp4")
    except ffmpeg.Error as e:
        print(f"An error occurred: {e.stderr.decode()}")

def recognize_song() -> tuple:
    """
    Recognizes song from WAV file.

    Returns:
        (str): Song title.
        (str): Song artist.
    """

    url = f"https://{ACR_HOST}/v1/identify"

    timestamp = str(int(time.time()))
    http_method = "POST"
    http_uri = "/v1/identify"
    signature_version = "1"

    string_to_sign = f"{http_method}\n{http_uri}\n{api_keys["ACR_ACCESS_KEY"]}\naudio\n{signature_version}\n{timestamp}"
    signature = base64.b64encode(hmac.new(api_keys["ACR_ACCESS_SECRET"].encode("utf-8"), string_to_sign.encode("utf-8"), hashlib.sha1).digest()).decode("utf-8")

    data = {
        "access_key": api_keys["ACR_ACCESS_KEY"],
        "sample_bytes": os.path.getsize("temp.wav"),
        "timestamp": timestamp,
        "signature": signature,
        "data_type": "audio",
        "signature_version": "1"
    }

    # Read WAV file as binary
    with open("temp.wav", "rb") as f:
        files = {"sample": f}
        response = requests.post(url, data=data, files=files)

    # Parse response
    result = response.json()
    os.remove("temp.wav")
    if "metadata" in result and "music" in result["metadata"]:
        song_data = result["metadata"]["music"][0]
        return song_data["title"], song_data["artists"][0]["name"]
    return None, None

def get_spotify_url(title: str, artist: str) -> str:
    """
    Generates a Spotify search link for the given song title and artist.

    Args:
        title (str): The title of the song.
        artist (str): The artist of the song.

    Returns:
        str: Spotify search URL.
    """

    query = f"{title} {artist}"
    encoded_query = urllib.parse.quote(query)
    url = f"https://open.spotify.com/search/{encoded_query}"
    return url


def get_youtube_music_url(title: str, artist: str) -> str:
    """
    Generates a YouTube Music search link for the given song title and artist.

    Args:
        title (str): The title of the song.
        artist (str): The artist of the song.

    Returns:
        str: YouTube Music search URL.
    """

    query = f"{title} {artist}"
    encoded_query = urllib.parse.quote(query)
    url = f"https://music.youtube.com/search?q={encoded_query}"
    return url


def get_apple_music_url(title: str, artist: str) -> str:
    """
    Generates an Apple Music search link for the given song title and artist.

    Args:
        title (str): The title of the song.
        artist (str): The artist of the song.

    Returns:
        str: Apple Music search URL.
    """

    query = f"{title} {artist}"
    encoded_query = urllib.parse.quote(query)
    url = f"https://music.apple.com/us/search?term={encoded_query}"
    return url

def write_output(title : str, artist : str) -> None:
    with open("out.txt", "w") as f:
        if not title and not artist:
            f.write("f")
            print("Song not recognized")
        else:
            print(f"\nTitle: {t}\nArtist: {a}\n")
            print(get_spotify_url(t, a))
            f.write("t\n")
            f.write(f"{title}\n")
            f.write(f"{artist}\n")
            f.write(f"{get_spotify_url(title, artist)}\n")
            f.write(f"{get_youtube_music_url(title, artist)}\n")
            f.write(f"{get_apple_music_url(title, artist)}\n")

if __name__ == "__main__":
    # API keys
    ACR_HOST = "identify-us-west-2.acrcloud.com"
    api_keys = load_api_keys("keys.txt")

    # Finding the song
    download_video("https://www.instagram.com/reels/DGw64Z4S1hb/")
    mp4_to_wav()

    # Creating output file
    t, a = recognize_song()
    write_output(t, a)