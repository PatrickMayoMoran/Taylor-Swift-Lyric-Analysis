"""
I am trying to scrape T Swift lyrics to then do analysis!
I am using requests to get the URL and beautiful soup to parse the html.
I have defined as constants the Album names, Album years, and album class (a tag in the html).
With this website - https://www.azlyrics.com/t/taylorswift.html - songs and album names
are all siblings on the same html level.
Songs do not have any tag identifying them as part of an album (that I could see).
Songs are simply listed under their album.
Every song has a link to its own page where the lyrics are located.
My goal is thus:
 1) to get only the songs/links I want by album
 2) to then get the lyrics from each of these songs
 3) to analyze lyrics
 4) display/share results

At this point, just accomplishing 1 & 2 is a big accomplishment.
3 & 4 are stretch goals to learn about and return to.

"""

import requests
from bs4 import BeautifulSoup

ALBUMS = ['Taylor Swift', 'Fearless', 'Speak Now', 'Red', '1989', 'Reputation', 'Lover']
ALBUM_YEARS = ['2006', '2008', '2010', '2012', '2014', '2017', '2019']
ALBUM_CLASS = 'class="album"'
SONG_CLASS = 'class="listalbum-item"'
LYRICS_URL = "https://www.azlyrics.com/t/taylorswift.html"
tswift_lyrics = {} #I think I use this as a global variable? Which I don't understand whether this is good or bad... but it works!
#Is my alternative making an empty dictionary in main and passing it down as an argument in all the functions as well as returning it back?
SONG_SPLIT_1 = '<!-- Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement. Sorry about that. -->'
SONG_SPLIT_2 = '</div>\n<br/><br/>'
PUNCTUATION = '.!?,-():;\'"' #added double quotes and parentheses

def main():
    #tswift_lyrics = {} I thought this would create an accessible dictionary in all sub functions but was mistaken!
    make_lyric_dict()
    #print(tswift_lyrics)
    create_lyric_files()


def create_lyric_files():
    listed_lyrics = list(tswift_lyrics.keys())
    for song in listed_lyrics:
        link = get_song_link(song)
        song_lyrics = get_song_lyrics(link)
        write_lyric_file(song, song_lyrics)


def write_lyric_file(song, song_lyrics):
    #song is soup item we will get_text() from for song title
    #Need to get album title from dictionary with song as key
    #create name of file as album + song title
    album_name = get_album_name(song)
    song_name = song.get_text()
    file_name = album_name + ' ' + song_name + '.txt'
    print(file_name)
    outfile = open(file_name, 'w')
    outfile.write(song_lyrics)
    outfile.close()


def get_album_name(song):
    album_name = tswift_lyrics.get(song)
    return album_name

def get_song_link(song):
    song = str(song)
    url_split = song.split(sep='<a href="')
    link_messy_list = url_split[1].split(sep='" target')
    link_messy = link_messy_list[0]
    link_clean = link_messy.replace('..', 'https://www.azlyrics.com')
    return link_clean

def get_song_lyrics(link):
    html_lyrics = requests.get(link)
    soup_lyrics = BeautifulSoup(html_lyrics.content, 'html.parser')
    song_lyrics = create_lyric_string(soup_lyrics)
    return song_lyrics

def create_lyric_string(soup_lyrics):
    string_lyrics_mush = str(soup_lyrics)
    lyric_mush = string_lyrics_mush.split(sep=SONG_SPLIT_1)
    lyric_mush_half = lyric_mush[1]
    split_lyric_mush_half = lyric_mush_half.split(sep=SONG_SPLIT_2)
    just_lyrics = split_lyric_mush_half[0]
    lyrics_without_breaks = just_lyrics.replace('<br/>', '')
    lyrics_true = remove_punctuation(lyrics_without_breaks)
    lowercase_lyrics = lyrics_true.lower()
    return lowercase_lyrics


def remove_punctuation(lyrics_without_breaks):
    result = ''
    for char in lyrics_without_breaks:
        if char not in PUNCTUATION:
            result += char
    return result




"""
This function will start by getting all the lyrics from T-Sweezy's 7 albums
"""
def make_lyric_dict():
    lyrics_webpage = get_url(LYRICS_URL)

    # This line turns the html into a beautiful soup object
    lyrics_soup = BeautifulSoup(lyrics_webpage.content, 'html.parser')


    #The below line gets the ordered list of albums/songs from the website.
    music_list = get_music_list(lyrics_soup)
    for item in music_list:
        if is_good_album(item):
            #print("Album tested good!")
            get_album_songs(item, music_list)
        #else: #I wrote this while testing this loop
            #print("album test failed")


"""
Below function is me beginning decomposition.
This function should test if item in music_list is an album we want.
"""
def is_good_album(item):
    item_string = str(item)
    check = any(album_year in item_string for album_year in ALBUM_YEARS)
    if check:
        #print(item.get_text())
        #check = any(album_year in item_string for album_year in ALBUM_YEARS)
        #print(check)
        return check

"""
This function gets the html webpage from chosen url.
"""
def get_url(lyrics_url):
    return requests.get(lyrics_url)

"""
This function sorts the beautiful soup object for songs and albums.
"""
def get_music_list(lyrics_soup):
    music_list = lyrics_soup.find_all('div', class_=['album', 'listalbum-item'])
    return music_list

"""
This function gets all the songs for a given album and assigns them to a dictionary.
Song title is the key, album is the value.
"""
def get_album_songs(item, music_list):
    album_index = music_list.index(item)
    next_item = album_index + 1
    song_status = is_song(music_list[next_item])
    #tswift_lyrics = {} #Thought about initializing here and passing it back, but then each new call would erase previous work
    while song_status == True:
        #print("yay!") #testing
        dict_value = music_list[album_index].get_text()
        popped_song = music_list.pop(next_item)
        tswift_lyrics[popped_song] = dict_value
        #print(tswift_lyrics)
        song_status = is_song(music_list[next_item])
    #print(tswift_lyrics)

"""
This function tests whether an item is a song or not.
"""
def is_song(indexed_item):
    str_item = str(indexed_item)
    if SONG_CLASS in str_item:
        #print("yay, a song!") #I used this while testing
        return True
    else:
        return False


if __name__ == '__main__':
    main()