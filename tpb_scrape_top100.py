import logging
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

from local_settings import OMDB_APIKEY
from utils import log


@log
def get_soup_of_html_page(url):
    """Takes a url and does a request to get the html page.
    The html pages gets processed into a beautiful soup object."""
    html_page = requests.get(url).text
    soup = BeautifulSoup(html_page, 'html.parser')
    return soup


@log
def get_movie_info_from_element(html_element):
    """Takes element from tpb page and extracts title and url from it
    Also creates a cleaner title than the piratebay title."""
    tpb_title = html_element.get_text()
    logging.info(f'Extracting info from html element {tpb_title}')

    tpb_movie_url = html_element.get('href')
    tpb_clean_title = re.search('(.*?)\d.*', tpb_title).group(1).replace('.', ' ').strip('(').strip().strip('-')

    tpb_movie_info = {
        'tpb_title': tpb_title,
        'tpb_movie_url': tpb_movie_url,
        'tpb_clean_title': tpb_clean_title,
    }

    return tpb_movie_info


@log
def get_movie_info_from_omdb(title, apikey=OMDB_APIKEY):
    """Does an api request to OMDB to search for a movie.
    You can do 1000 requests per day with this key.
    OMDB api returns a json from which I take the necessary movie info fields.
    If movie not found, this function returns an empty dictionary."""
    title_for_omdb_query = title.replace(' ', '+')
    omdb_url_query = f'http://www.omdbapi.com/?t={title_for_omdb_query}&type=movie&apikey={apikey}'
    omdb_search = requests.get(omdb_url_query).json()

    if omdb_search['Response'] == 'True':
        omdb_movie_info = {
            'title': omdb_search['Title'],
            'genre': omdb_search['Genre'],
            'plot': omdb_search['Plot'],
            'rating': omdb_search['imdbRating'],
            'metascore': omdb_search['Metascore'],
            'imdb_id': omdb_search['imdbID'],
            'imdb_url': f"https://www.imdb.com/title/{omdb_search['imdbID']}/",
            'type': omdb_search['Type'],
            'image_url': omdb_search['Poster'],
            'votes': omdb_search['imdbVotes'].replace(',', ''),
        }
    else:
        omdb_movie_info = {}

    return omdb_movie_info


@log
def get_data_from_elements(elements):
    """Iterates over all relevant elements from tpb top 100 page and
    gets all relevant movie info from tpb itself and omdb."""
    top_movies = {}

    for nr, movie_html_element in enumerate(elements):
        logging.info(f'Getting data from element {nr}')

        tpb_movie_info = get_movie_info_from_element(movie_html_element)
        omdb_movie_info = get_movie_info_from_omdb(tpb_movie_info['tpb_clean_title'])

        movie_data = {**tpb_movie_info, **omdb_movie_info}  # python>=3.5 solution

        top_movies[nr] = movie_data

    return top_movies


@log
def get_top100_movies():
    """Scrape tpb top 100 movie page and get relevant info about all those movies.
    Returns the top 100 movies + relevant info."""
    top100_soup = get_soup_of_html_page('https://thepiratebay.org/top/201')
    top100_elements = top100_soup.find_all('a', class_='detLink')
    top100_movies = get_data_from_elements(top100_elements)

    logging.info('Creating pandas dataframe')
    df_top100 = pd.DataFrame.from_dict(top100_movies, orient='index')

    logging.info('Output results to csv')
    df_top100.to_csv('top100movies.csv', index=False)


if __name__ == '__main__':
    logging.info('Starting main app')
    get_top100_movies()

