import requests
import json
import re
from bs4 import BeautifulSoup

def get_genius_api_key():
    #https://docs.genius.com/
    return "YOUR_API_KEY"


def search_genius(query, api_key):
    base_url = "https://api.genius.com"
    headers = {"Authorization": "Bearer " + api_key}
    search_url = f"{base_url}/search?q={query}"
    response = requests.get(search_url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.status_code)
        return None

""" def get_lyrics_from_url(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    lyrics = soup.find("div", class_=re.compile("Lyrics__Container"))
    if lyrics is not None:
        for br in lyrics.find_all("br"):
            br.replace_with("\n")
        formatted_lyrics = re.sub(r'\[.*?\]', '', lyrics.get_text().strip())
        return formatted_lyrics
    else:
        return "Lyrics not found." """
    
def get_lyrics_from_url(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    lyrics_containers = soup.find_all("div", class_=re.compile("Lyrics__Container"))

    if lyrics_containers:
        combined_lyrics = ""

        for lyrics in lyrics_containers:
            for br in lyrics.find_all("br"):
                br.replace_with("\n")
            formatted_lyrics = re.sub(r'\[.*?\]', '', lyrics.get_text().strip())
            combined_lyrics += formatted_lyrics + "\n"

        return combined_lyrics.strip()
    else:
        return "Lyrics not found."

    
def count_unique_words(lyrics):
    # Remove punctuation except apostrophes
    cleaned_lyrics = re.sub(r"[^\w\s']", '', lyrics.lower())
    #extract words with '  etc \b\w+('\w|)\b
    # Extract words and count unique words
    #word_list = re.findall(r"\b\w+('\w|)\b", cleaned_lyrics)
    word_list = re.findall(r"\b\w+(?:'\w+)?\b", cleaned_lyrics)
    
    unique_words = set(word_list)
    #print(unique_words)
    return len(unique_words)

def get_artist_songs(artist_id, api_key):
    base_url = "https://api.genius.com"
    headers = {"Authorization": "Bearer " + api_key}
    songs = []

    page = 1
    while True:
        search_url = f"{base_url}/artists/{artist_id}/songs?per_page=50&page={page}"
        response = requests.get(search_url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            songs.extend(data["response"]["songs"])

            if len(data["response"]["songs"]) < 50:
                break
            else:
                page += 1
        else:
            print("Error:", response.status_code)
            break

    return songs

def main():
    
    api_key = get_genius_api_key()
    menu = input("1:) Enter artist name or song\n2:) Enter aritist to get total count of unique words\n3:) Exit\n")

    if menu == "1":
        # search for artist OR song name  
        query = input("Enter the song title or artist name: ")
        search_result = search_genius(query, api_key)

        if search_result:
            hits = search_result["response"]["hits"]
            for hit in hits:
                title = hit["result"]["title"]
                artist = hit["result"]["primary_artist"]["name"]
                lyrics_url = hit["result"]["url"]
                songid = hit["result"]["id"]
                artistid = hit["result"]["primary_artist"]["id"]
                lyrics = get_lyrics_from_url(lyrics_url)
                
                print(f"\nTitle: {title}\nArtist: {artist}\nArtist ID: {artistid}\nLyrics URL: {lyrics_url}\nSong ID: {songid}\n")
                print("Lyrics:")
                print(lyrics)
                print("-" * 80)

                unique_word_count = count_unique_words(lyrics)
                print(f"Unique word count: {unique_word_count}")

                proceed = input("\nDo you want to continue with the next result? (yes/no): ").strip().lower()
                if proceed != "yes" and proceed != "y":
                    break
        else:
            print("No results found.")#
    elif menu == "2":
        #search for artist and get their total unique words across catalog
        query = input("Enter the song title or artist name: ")
        search_result = search_genius(query, api_key)

        if search_result:
            hits = search_result["response"]["hits"]
            artist_id = hits[0]["result"]["primary_artist"]["id"]

            songs = get_artist_songs(artist_id, api_key)
            combined_lyrics = ""

            for song in songs:
                title = song["title"]
                artist = song["primary_artist"]["name"]
                songid = song["id"]
                artistid = song["primary_artist"]["id"]
                lyrics_url = song["url"]
                

                print(f"\nTitle: {title}\nArtist: {artist}\nArtist ID: {artistid}\nLyrics URL: {lyrics_url}\nSong ID: {songid}\n")
                lyrics = get_lyrics_from_url(lyrics_url)
                unique_word_count = count_unique_words(lyrics)
                print("Lyrics:")
                print(lyrics)
                print("\n")
                print(f"Unique word count: {unique_word_count}")
                print("-" * 80)

                combined_lyrics += "\n" + lyrics

            unique_word_count = count_unique_words(combined_lyrics)
            print(f"\nUnique word count across the artist's catalog: {unique_word_count}")
            print(f"\nNumber of songs: {len(songs)}")


        else:
            print("No results found.")
    elif menu == "3":
        print("exiting")

if __name__ == "__main__":
    main()
