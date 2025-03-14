import os
import time
import hmac
import hashlib
import base64
import requests
import urllib.parse
import yt_dlp
from PIL import Image
from io import BytesIO

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

    if len(keys) != 3:
        raise ValueError(
            "Invalid key file format. Ensure 3 lines: ACRCloud Host URL, ACRCloud Client Key, ACRCloud Secret Key.")

    return {
        "ACR_HOST" : keys[0],
        "ACR_ACCESS_KEY": keys[1],
        "ACR_ACCESS_SECRET": keys[2]
    }

def download_video(url : str, error: list) -> None:
    """
    Scrapes video from either Reels, YT Shorts, or TikTok and writes to working directory.

    Args:
        url (str): URL to video from Reels, YT Shorts, or TikTok.
        error (list): List to store error messages.
    """

    try:
        if "youtube.com" in url or "youtu.be" in url:
            if "shorts" not in url: # YouTube Shorts only
                print("Not a YouTube Shorts link.")
                error.append("Only YouTube SHORTS links are supported at the moment.")
                return

        # yt-dlp options
        ydl_opts = {
            "outtmpl": os.path.join("output", "temp.%(ext)s"),  # Ensure correct extension
            "format": "bestaudio/best",  # Get the best audio format available
            "quiet": True,  # Suppress logs
            "noprogress": True,  # Hide progress bar
            "overwrites": True,  # Overwrite existing file
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",  # Convert to WAV
                "preferredquality": "0"  # Best quality
            }]
        }

        print(f"Downloading video...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        print("Download successful.")

    except:
        error.append("Invalid URL. Please enter a valid TikTok, Instagram Reels, or YouTube Shorts URL.")
        print("Invalid URL.")

def recognize_song(error: list) -> tuple:
    """
    Recognizes song from WAV file.

    Returns:
        (str): Song title.
        (str): Song artist.
    """

    api_keys = load_api_keys("keys.txt")
    url = f"https://{api_keys["ACR_HOST"]}/v1/identify"

    timestamp = str(int(time.time()))
    http_method = "POST"
    http_uri = "/v1/identify"
    signature_version = "1"

    string_to_sign = f"{http_method}\n{http_uri}\n{api_keys["ACR_ACCESS_KEY"]}\naudio\n{signature_version}\n{timestamp}"
    signature = base64.b64encode(hmac.new(api_keys["ACR_ACCESS_SECRET"].encode("utf-8"), string_to_sign.encode("utf-8"), hashlib.sha1).digest()).decode("utf-8")

    data = {
        "access_key": api_keys["ACR_ACCESS_KEY"],
        "sample_bytes": os.path.getsize("output/temp.wav"),
        "timestamp": timestamp,
        "signature": signature,
        "data_type": "audio",
        "signature_version": "1"
    }

    print("Analyzing song...")

    # Read WAV file as binary
    with open("output/temp.wav", "rb") as f:
        files = {"sample": f}
        response = requests.post(url, data=data, files=files)

    # Parse response
    result = response.json()
    os.remove("output/temp.wav")
    if "metadata" in result and "music" in result["metadata"]:
        song_data = result["metadata"]["music"][0]
        print("Song found.")
        return song_data["title"], song_data["artists"][0]["name"]
    error.append("NO_SONG_FOUND")
    return None, None

def fetch_album_cover(song_name: str, artist_name: str) -> bool:
    """
    Gets an album cover given a song's title and artist using the iTunes API.

    Args:
        song_name (str): The name of the song.
        artist_name (str): The name of the artist.

    Returns:
        (bool) True if the album cover was found and saved, False otherwise.
    """
    base_url = "https://itunes.apple.com/search"

    # Parameters for search
    params = {
        "term": f"{song_name} {artist_name}",
        "media": "music",
        "limit": 1
    }

    try:
        # Fetches request
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        if data["resultCount"] > 0:
            album_cover_url = data["results"][0].get("artworkUrl100", "").replace("100x100bb", "600x600bb")
            if album_cover_url:
                image_response = requests.get(album_cover_url, stream=True)
                image_response.raise_for_status()

                image = Image.open(BytesIO(image_response.content))
                image = image.resize((140, 140), Image.LANCZOS)

                image.save("../media/cover.jpg", "JPEG")

                print("Album cover saved.")
                return True

        print("No album cover found.")
        return False

    except requests.RequestException as e:
        print(f"Error fetching album cover: {e}")
        return False

# TODO: Function to get most vibrant color in the album cover

def get_song_urls(title: str, artist: str) -> tuple:
    """
    Generates a Spotify, YouTube Music, and Apple Music search link for the given song title and artist.

    Args:
        title (str): The title of the song.
        artist (str): The artist of the song.

    Returns:
        tuple: Spotify, YouTube Music, and Apple Music search links.
    """

    query = f"{title} {artist}"
    encoded_query = urllib.parse.quote(query)

    return (
        f"https://open.spotify.com/search/{encoded_query}",
        f"https://music.youtube.com/search?q={encoded_query}",
        f"https://music.apple.com/us/search?term={encoded_query}"
        )

def generate_output(title: str, artist: str, error: list) -> dict:
    """
    Tries to make a dictionary with the song data.

    Args:
        title (str): The title of the song.
        artist (str): The artist of the song.
        error (list): List to store error messages.

    Returns:
        dict: A dictionary containing the song data.
    """

    if title and artist:
        urls = get_song_urls(title, artist)
        return {
            "success": True,
            "title": title,
            "artist": artist,
            "spotify": urls[0],
            "youtube": urls[1],
            "apple": urls[2]
        }
    else:
        return {
            "success": False,
            "error": error[0]
        }

def main(url):
    error_msg = []
    t, a = None, None

    # Generating WAV file
    download_video(url, error_msg)

    # Retrieving and return song data if no errors
    if len(error_msg) == 0:
        t, a = recognize_song(error_msg)

    return generate_output(t, a, error_msg)