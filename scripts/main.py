import os
import time
import hmac
import hashlib
import base64
import requests
import urllib.parse
import yt_dlp

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

    except Exception as e:
        print(f"An error occurred: {e}")

def recognize_song() -> tuple:
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
        print(song_data)
        print("Song found.")
        return song_data["title"], song_data["artists"][0]["name"]
    return None, None

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

def write_output(title : str, artist : str) -> None:
    """
    Writes song data to out.txt in the working directory.

    Args:
        title (str): The title of the song.
        artist (str): The artist of the song.
    """

    with open("output/out.txt", "w") as f:
        if not title and not artist:
            f.write("f")
            print("Song not recognized")
        else:
            print("Fetching song data...")
            urls = get_song_urls(title, artist)

            f.write("t\n")
            f.write(f"{title}\n")
            f.write(f"{artist}\n")
            f.write(f"{urls[0]}\n")
            f.write(f"{urls[1]}\n")
            f.write(f"{urls[2]}\n")
            print("Done.")

def main(url):
    # Generating WAV file
    download_video(url)

    # Retrieving and writing song data
    t, a = recognize_song()
    write_output(t, a)

if __name__ == "__main__":
    main("https://www.instagram.com/p/DGTK_b2PuX_/")