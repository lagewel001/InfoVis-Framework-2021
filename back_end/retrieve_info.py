import numpy as np
import pandas as pd
import wikipedia

from colour import Color

from .data import *

ART_PERIODS = [
    {"name": "Medieval art", "timeRange": [500, 1400]},
    {"name": "Renaissance", "timeRange": [1400, 1500]},
    {"name": "Mannerism", "timeRange": [1527, 1580]},
    {"name": "Baroque", "timeRange": [1600, 1750]},
    {"name": "Rococo", "timeRange": [1699, 1780]},
    {"name": "Neoclassicism", "timeRange": [1750, 1850]},
    {"name": "Romanticism", "timeRange": [1780, 1850]},
    {"name": "Realism", "timeRange": [1848, 1900]},
    {"name": "Art Nouveau", "timeRange": [1890, 1910]},
    {"name": "Impressionism", "timeRange": [1865, 1885]},
    {"name": "Post-impressionism", "timeRange": [1885, 1910]},
    {"name": "Fauvism", "timeRange": [1900, 1935]},
    {"name": "Expressionism", "timeRange": [1905, 1920]},
    {"name": "Cubism", "timeRange": [1907, 1914]},
    {"name": "Surrealism", "timeRange": [1917, 1950]},
    {"name": "Modern art", "timeRange": [1950, 2022]},
]


'''
# for example: http://127.0.0.1:5000/info/impressionism/1943/
# year is nodig om genre te bepalen naderhand want die staan niet in dataset
def retrieve_info(genre, year):
    year = float(year)
    ranges = float(1)
    dictionary = {}

    w = wikipedia.page(genre)
    dictionary['genre'] = w.title

    dictionary['summary'] = wikipedia.summary(genre, sentences=3)

    # other art pieces created in same year
    year_df = model_data.loc[model_data['creation_year'].astype('float') < year+ranges]
    year_df = year_df.loc[year_df['creation_year'].astype('float') > year-ranges]

    year_list = pd.Series.tolist(year_df['artwork_name'])
    if len(year_list) < 5:
        dictionary['same_year/genre'] = pd.Series.tolist(year_df['artwork_name'])
    else:
        dictionary['same_year/genre'] = pd.Series.tolist(year_df['artwork_name'])[:5]

    dictionary['related_terms'] = wikipedia.search(genre)

    # other = paintings.loc[paintings['artist_full_name'] == artist]

    return dictionary
'''


def _get_artist_histograms(model_data, artists=None):
    assert artists

    result = {}

    for artist in artists:
        data = pd.DataFrame()

        # Gather all works by this artist.
        works = model_data[model_data.artist_last_name == artist]
        # colors = works.color_pallete.dropna()
        colors = works.dominant_color.dropna()

        # The data are a series of strings. These strings represent a list of
        # hex codes. We use `eval` to convert these strings to lists.
        # colors = itertools.chain.from_iterable(
        #     eval(f"[{','.join(colors.values)}]")
        # )
        data['hue'] = [Color(col).hue for col in colors]
        data['year'] = [int(eval(year)) for year in works.creation_year]

        hues = []

        for year in sorted(data.year.unique()):
            hues.append(data[data.year == year].hue.median())

        if len(hues) == 0:
            continue

        hist, edges = np.histogram(
            hues,
            bins=10,
            range=(0, 1),
            density=True,
        )

        # result[artist] = list(zip(x_values, hist))
        result[artist] = list(hist)

    return result


def _get_period_histograms(model_data, year):
    print("Histogram of year", year)
    period = get_period(year)
    start, end = period['timeRange']

    data = model_data.dropna(subset=["creation_year"]).reset_index()

    creation_years = pd.Series([
        int(eval(year)) for year in data.creation_year
    ])
    data = data[creation_years >= start].reset_index()

    creation_years = pd.Series([
        int(eval(year)) for year in data.creation_year
    ])
    works = data[creation_years < end]

    # colors = works.color_pallete.dropna()
    colors = works.dominant_color.dropna()

    # The data are a series of strings. These strings represent a list of
    # hex codes. We use `eval` to convert these strings to lists.
    # colors = itertools.chain.from_iterable(
    #     eval(f"[{','.join(colors.values)}]")
    # )
    hue_data = pd.DataFrame({
        'hue': [Color(col).hue for col in colors],
        'year': [int(eval(year)) for year in works.creation_year]
    })

    hues = []

    for year in sorted(hue_data.year.unique()):
        hues.append(hue_data[hue_data.year == year].hue.median())

    hist, edges = np.histogram(
        hues,
        bins=10,
        range=(0, 1),
        density=True,
    )

    result = {
        period['name']: list(hist)
    }
    return result


def get_period(year):
    """
    Retrieve the period that a given year falls into.
    """
    for period in ART_PERIODS:
        start, end = period['timeRange']
        if start <= year < end:
            return period
    else:
        raise ValueError(
            f"Year {year} does not fall in any known art period!"
        )
