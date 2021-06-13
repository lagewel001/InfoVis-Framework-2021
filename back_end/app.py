import binascii
import numpy as np
import pandas as pd
import pickle
import scipy
import sys
import torch
import wikipedia
import urllib.request
import random

from base64 import encodebytes
from colour import Color
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from io import BytesIO
from PIL import Image
from scipy import cluster

from .retrieve_info import (
    _get_artist_histograms,
    _get_period_histograms,
    get_period,
)
from .data import model_data, all_artists, _get_timeline_data
from .GAN import dnnlib, generate

sys.path.append("./GAN/")


if torch.cuda.is_available():
    DEVICE = torch.device('cuda')
# else:
#     DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    with dnnlib.util.open_url("./GAN/models/artists.pkl") as f:
        G_artists = pickle.Unpickler(f).load()['G_ema'].to(DEVICE)

    with dnnlib.util.open_url("./GAN/models/centuries.pkl") as f:
        G_centuries = pickle.Unpickler(f).load()['G_ema'].to(DEVICE)

NUM_CLUSTERS = 4
RESIZE = 150  # Size of images for clustering.

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins='*')

WIKI_NAME_MAP = {
    "eyck": "Jan van Eyck",
    "vinci": "Leonardo da Vinci",
    "bosch": "Jheronimus Bosch",
    "hals": "Frans Hals",
    "greco": "El Greco",
    "dyck": "Anthony van Dyck",
    "rijn": "Rembrandt",
    "steen": "Jan Steen",
    "blake": "William Blake",
    "turner": "J. M. W. Turner",
    "delacroix": "Eugène Delacroix",
    "gogh": "Vincent van Gogh"
}


def detect_colors(image):
    image = image.resize((RESIZE, RESIZE))

    array = np.asarray(image.convert('RGB'))
    shape = array.shape

    array = array.reshape(scipy.product(shape[:2]), shape[2]).astype(float)

    codes, dist = cluster.vq.kmeans(array, NUM_CLUSTERS)

    vecs, dist = cluster.vq.vq(array, codes)
    counts, bins = scipy.histogram(vecs, len(codes))

    total = np.sum(np.array(counts))
    percentages = (counts / total)

    color_list = []
    for code in codes:
        hex_color = binascii.hexlify(bytearray(
            int(c) for c in code
        )).decode('ascii')
        color_list.append(f"#{hex_color}")

    dom_code = codes[scipy.argmax(counts)]
    dom_hex = binascii.hexlify(bytearray(
        int(c) for c in dom_code
    )).decode('ascii')
    dom_color = f"#{dom_hex}"

    colors = color_list

    return list(colors), list(percentages), dom_color


def retrieve_info(genre):
    dictionary = {}

    print("Retrieving info for genre", repr(genre))

    if isinstance(genre, int):
        period = get_period(genre)
        genre = period['name']
    else:
        genre = WIKI_NAME_MAP.get(genre, genre)

    dictionary = {
        'genre': genre,
        'summary': wikipedia.summary(
            genre, sentences=2, auto_suggest=False
        ),
        'related_terms': wikipedia.search(genre),
    }

    return dictionary


def get_artists(model_data):
    all_artist_text = sorted(
        model_data['school'].astype(str).unique().tolist()
    )

    return all_artist_text


def get_scatter_data(model_data, label, is_artist=True):
    """
    Collect data for the school/dominant color linechart.
    """
    series = []

    if is_artist:
        data = model_data[model_data.artist_last_name == label]
    else:
        period = get_period(int(label))
        start, end = period['timeRange']

        data = model_data.dropna(subset=["creation_year"]).reset_index()
        creation_years = pd.Series([
            int(eval(year)) for year in data.creation_year
        ])
        data = data[creation_years >= start].reset_index()

        creation_years = pd.Series([
            int(eval(year)) for year in data.creation_year
        ])
        data = data[creation_years < end]

        label = period['name']

    data = data[['creation_year', 'dominant_color']]
    data = data.sort_values(by='creation_year')
    data['hue'] = [Color(color).hue for color in data.dominant_color.dropna()]

    values = []
    styles = []

    # For years with more than one work that year, we take the average
    # hue of all the dominant colors in that year.
    for year in data.creation_year.unique():
        hue = data[data.creation_year == year].hue.median()
        color = Color(hue=hue, saturation=1, luminance=0.5)

        values.append((int(eval(year)), hue))
        styles.append(color.hex)

    series = {
        # 'styles': styles,
        'type': 'scatter',
        'text': label,
        'values': values,
        'marker': {'size': 3},
    }

    return series


def encode_image(image, format='png'):
    """
    Encode an image into base64 so it can be send along with an event.

    Parameters
    ----------
    image: PIL.Image
    format: str, default 'png'
    """
    stream = BytesIO()
    image.save(stream, format=format)
    encoded = encodebytes(stream.getvalue()).decode('ascii')

    return f"data:image/{format};base64, {encoded}"


@socketio.event
def collect_scatter_data(data):
    def get_trendline(values):
        """Fit a polynomial to the data."""
        x, y = zip(*values)
        weights = np.polyfit(x, y, 3)
        model = np.poly1d(weights)

        trend_x = np.linspace(min(x), max(x), 20)
        trend_y = model(trend_x)

        return trend_x, trend_y

    output = {
        'plot': {
            'marker': {},
        },
        'series': [],
    }

    for label in data['labels']:
        scatter = get_scatter_data(
            model_data, label, is_artist=data['type'] == "artist",
        )

        trend_x, trend_y = get_trendline(scatter['values'])

        trendline = {
            'text': f"{scatter['text']} trend",
            'values': list(zip(trend_x, trend_y)),
            'type': 'line',
            'aspect': 'spline',
            'marker': {'visible': False},
            'line-width': 2,
            # 'line-style': "dashed",
            # 'line-color': "black",
        }

        output['series'].append(scatter)
        output['series'].append(trendline)

    socketio.emit("collect_scatter_data", output)


def get_image(class_idx, class_type):
    if class_type == "centuries":
        century = int(class_idx / 100)
        data = model_data.loc[
            model_data['creation_year'].str[:2] == str(century)
        ]
        urls = data['image_url'].tolist()[:6]
        nr = random.randint(0, len(data)-1)
        data = data.iloc[nr]
        # data = model_data['creation_year' == class_idx][0]
        image_url = data['image_url']
        title = data['artwork_name']
        artist = data['artist_last_name']
        year = data['creation_year']

    elif class_type == "artists":
        data = model_data.loc[model_data['artist_last_name'] == class_idx]
        urls = data['image_url'].tolist()[:6]
        nr = random.randint(0, len(data)-1)
        data = data.iloc[nr]
        image_url = data['image_url']
        title = data['artwork_name']
        artist = class_idx
        year = data['creation_year']

    return urls, image_url, title, artist, year


@socketio.event
def collect_info(data):
    class_type = data['type']
    class_idx = data['class_idx']
    side = data['compare_side']

    print("Collecting info", class_type, class_idx)
    urls, url, title, artist, year = get_image(class_idx, class_type)

    try:
        image = Image.open(urllib.request.urlopen(url))
    except urllib.error.HTTPError:
        print(f"Could not download image at url '{url}'.")
        image = Image.new('RGB', (1, 1))

    colors, percentages, dom_color = detect_colors(image)

    socketio.emit("set_image", {
        "existend_imgs": urls,
        "compare_side": side,
        "title": title,
        "artist": artist,
        "year": year,
        "colors": {
            'dominant_color': dom_color,
            'color_palette': colors,
            'color_distribution': percentages,
        },
    })

    summary = retrieve_info(class_idx)
    socketio.emit("get_summary", {
        "compare_side": side,
        "genre": summary['genre'],
        "summary": summary['summary'],
        "related_terms": summary['related_terms'],
    })


@socketio.event
def collect_info2(data):
    class_type = data["type"]
    class_idx = data["class_idx"]
    compare = data['compare']

    class_idx2 = data["class_idx2"]

    title2 = False
    artist2 = False
    year2 = False
    image_list2 = False

    print("Collecting info", class_type, class_idx)

    # Load a placeholder image.
    # TODO: Obtain a generated image here.
    image_list, url, title, artist, year = get_image(class_idx, class_type)

    try:
        image = Image.open(urllib.request.urlopen(url))
    except urllib.error.HTTPError:
        print(f"Could not download image at url '{url}'.")
        image = Image.new('RGB', (1, 1))

    # Encode the image for the response.
    img_stream = BytesIO()
    image.save(img_stream, format="png")

    if compare:
        image_list2, image2, title2, artist2, year2 = get_image(
            class_idx2, class_type
        )
        image2 = Image.open(urllib.request.urlopen(image2))
        # Encode the image for the response.
        img_stream2 = BytesIO()
        image2.save(img_stream2, format="png")

    socketio.emit("set_image", {
            "existend_imgs": image_list,
            "title": title,
            "artist": artist,
            "year": year,
            "existend_imgs2": image_list2,
            "title2": title2,
            "artist2": artist2,
            "year2": year2
        })

    # Get the primary color of the image.
    colors, percentages, dom_color = detect_colors(image)
    socketio.emit("change_color", dom_color)

    dictionary = retrieve_info(class_idx)
    dictionary2 = False
    if compare:
        colors2, percentages2, dom_color2 = detect_colors(image2)
        dictionary2 = retrieve_info(class_idx2)

    if compare:
        socketio.emit("get_summary", {
            "genre": dictionary['genre'],
            "genre2": dictionary2['genre'],
            "summary": dictionary['summary'],
            "related_terms": dictionary['related_terms'],
            "summary2": dictionary2['summary'],
            "related_terms2": dictionary2['related_terms']
        })
    else:
        socketio.emit("get_summary", {
            "genre": dictionary['genre'],
            "summary": dictionary['summary'],
            "related_terms": dictionary['related_terms'],
        })


@socketio.event
def generate_images(data):
    side = data['compare_side']

    if not torch.cuda.is_available():
        socketio.emit("images_generated", {
            "images": [],
            "seeds": [],
            "compare_side": side,
            "success": False,
            "message": "No Graphical Processing Unit available!"
        })
        return

    classification_type = data["type"]
    amount = data["amount"]
    class_idx = data["class_idx"]

    seeds = np.random.randint(0, 10000, amount)

    if classification_type == "artists":
        try:
            class_idx = generate.ARTIST_LABELS.index(class_idx)
        except ValueError:
            message = f"Label {repr(class_idx)} does not exist!"
            socketio.emit("images_generated", {
                "images": [],
                "seeds": [],
                "compare_side": side,
                "success": False,
                "message": message,
            })
            raise ValueError(message)

        images = generate.generate_images(G_artists, seeds, class_idx)
    elif classification_type == "centuries":
        # print(f"Generating painting from the {class_idx}th century")
        images = generate.generate_images(G_centuries, seeds, class_idx)
    else:
        message = f"Type {repr(classification_type)} is not known!"
        socketio.emit("images_generated", {
            "images": [],
            "seeds": [],
            "compare_side": side,
            "success": False,
            "message": message
        })
        raise ValueError(message)

    image_data = []

    for image in images:
        colors, percentages, dom_color = detect_colors(image)

        image_data.append({
            'image': encode_image(image),
            'dominant_color': dom_color,
            'color_palette': colors,
            'color_distribution': percentages,
        })

    socketio.emit("images_generated", {
        "images": image_data,
        "seeds": seeds.tolist(),
        "compare_side": side,
        "success": True,
        "message": ""
    })


@socketio.event
def get_timeline_data(artists=None, adding=False):
    timeline_data, artists = _get_timeline_data(artists, adding)
    return {
        'timelineData': timeline_data,
        'artists': artists
    }


@socketio.event
def get_all_artists():
    return all_artists


@socketio.event
def get_artist_histograms(data):
    labels = data['artists']

    if data['type'] == "artist":
        histograms = _get_artist_histograms(model_data, labels)
    else:
        histograms = _get_period_histograms(model_data, labels[0])

    socketio.emit("get_style_hists", {
        "series": [{
            "values": values,
            "text": key,
        } for key, values in histograms.items()],
    })


@socketio.on('connect')
def test_connect():
    print("Connected")


if __name__ == "__main__":
    socketio.run(app)
