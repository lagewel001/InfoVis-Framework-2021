import binascii
import numpy as np
import pickle
import scipy
import sys
import torch
import wikipedia
import urllib.request
import random
import json
import datetime

from base64 import encodebytes
from colour import Color
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from io import BytesIO
from PIL import Image
from scipy import cluster

from .retrieve_info import retrieve_info, _get_artist_histograms
from .data import model_data, all_artists, _get_timeline_data
from .GAN import dnnlib, generate
from datetimerange import DateTimeRange



# art_periods = [
#         {"name": "Medieval", "timeRange": DateTimeRange("500-01-01T10:00:00+0900", "1400-01-01T10:00:00+0900")},
#         {"name": "Renaissance", "timeRange": DateTimeRange("1400-01-01T10:00:00+0900", "1600-01-01T10:00:00+0900")},
#         {"name": "Mannerism", "timeRange": DateTimeRange("1527-01-01T10:00:00+0900", "1580-01-01T10:00:00+0900")},
#         {"name": "Baroque", "timeRange": [new Date(1600, 1, 1), new Date(1750, 1, 1)]},
#         {"name": "Rococo", "timeRange": [new Date(1699, 1, 1), new Date(1780, 1, 1)]},
#         {"name": "Neoclassicism", "timeRange": [new Date(1750, 1, 1), new Date(1850, 1, 1)]},
#         {"name": "Romanticism", "timeRange": [new Date(1780, 1, 1), new Date(1850, 1, 1)]},
#         {"name": "Realism", "timeRange": [new Date(1848, 1, 1), new Date(1900, 1, 1)]},
#         {"name": "Art Nouveau", "timeRange": [new Date(1890, 1, 1), new Date(1910, 1, 1)]},
#         {"name": "Impressionism", "timeRange": [new Date(1865, 1, 1), new Date(1885, 1, 1)]},
#         {"name": "Post-impressionism", "timeRange": [new Date(1885, 1, 1), new Date(1910, 1, 1)]},
#         {"name": "Fauvism", "timeRange": [new Date(1900, 1, 1), new Date(1935, 1, 1)]},
#         {"name": "Expressionism", "timeRange": [new Date(1905, 1, 1), new Date(1920, 1, 1)]},
#         {"name": "Cubism", "timeRange": [new Date(1907, 1, 1), new Date(1914, 1, 1)]},
#         {"name": "Surrealism", "timeRange": [new Date(1917, 1, 1), new Date(1950, 1, 1)]},
#         {"name": "Modern", "timeRange": [new Date(1950, 1, 1), new Date(2022, 1, 1)]},
#       ]

sys.path.append("./GAN/")


if torch.cuda.is_available():
    DEVICE = torch.device('cuda')

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

    array = np.asarray(image)
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
    # year = float(year)
    # ranges = float(1)
    dictionary = {}

    genre = WIKI_NAME_MAP[genre] if genre in WIKI_NAME_MAP else genre

    dictionary['summary'] = wikipedia.summary(genre, sentences=3, auto_suggest=False)

    # print('artworks in same time period:')
    # other art pieces created in same year
    # year_df = model_data.loc[model_data['creation_year'].astype('float') < year+ranges]
    # year_df = year_df.loc[year_df['creation_year'].astype('float') > year-ranges]

    # year_list = pd.Series.tolist(year_df['artwork_name'])
    # if len(year_list) < 5:
    #     dictionary['same_year/genre'] = pd.Series.tolist(year_df['artwork_name'])
    # else:
    #     dictionary['same_year/genre'] = pd.Series.tolist(year_df['artwork_name'])[:5]

    dictionary['related_terms'] = wikipedia.search(genre)

    # other = model_data.loc[model_data['artist_full_name'] == artist]

    return dictionary


def get_artists(model_data):
    all_artist_text = sorted(model_data['school'].astype(str).unique().tolist())

    return all_artist_text


def get_line_chart_artist(model_data, label):
    """
    Collect data for the school/dominant color linechart.
    """
    series = []

    data = model_data[model_data.artist_last_name == label]
    data = data[['creation_year', 'dominant_color']]
    data = data.sort_values(by='creation_year')
    data['hue'] = [Color(color).hue for color in data.dominant_color.dropna()]
    hues = data['hue']
    print("Scatter", len(hues), sorted(hues)[-5:])

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
def collect_line_chart(data):
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

    for artist in data['labels']:
        scatter = get_line_chart_artist(model_data, artist)

        trend_x, trend_y = get_trendline(scatter['values'])

        trendline = {
            'text': f"{artist} trend",
            'values':list(zip(trend_x, trend_y)),
            'type': 'line',
            'aspect': 'spline',
            'marker': {'visible': False},
            'line-width': 2,
            # 'line-style': "dashed",
            # 'line-color': "black",
        }

        output['series'].append(scatter)
        output['series'].append(trendline)

    socketio.emit("collect_line_chart", output)


def get_image(class_idx, class_type):
    # print('helloo')
    # print(model_data[:10])
    if class_type == "centuries":
        data = model_data.loc[model_data['creation_year'] == class_idx]  
        urls = data['image_url'].tolist()[:6]
        # urls = list(map(decode, urls))
        image_list = urls
        # image_list = json.dumps({"image_urls": urls,
        # "titles": data['artwork_name'],
        # "year": data['creation_year']
        # })
        nr = random.randint(0, len(data)-1)
        data = data['image_url'].iloc[nr]
        # data = model_data['creation_year' == class_idx][0]
        image_url = data['image_url']
        title = data['artwork_name']
        year = class_idx
        artist = data['artist_last_name']

    elif class_type == "artists":
        # print(model_data.loc[model_data['artist_last_name'] == class_idx])
        data = model_data.loc[model_data['artist_last_name'] == class_idx]
        urls = data['image_url'].tolist()[:6]
        # urls = list(map(decode, urls))
        image_list = urls
        # image_list = json.dumps({"image_urls": urls,
        # "titles": data['artwork_name'],
        # "year": data['creation_year']
        # })
        nr = random.randint(0, len(data)-1)
        data = data.iloc[nr]
        image_url = data['image_url']
        title = data['artwork_name']
        artist = class_idx
        year = data['creation_year']



        # data = model_data['artist_full_name' == class_idx][0]
    return image_list, image_url, title, artist, year


@socketio.event
def collect_info(data):
    # print("Hallo, ik kom hier om dingen volledig in de war te gooien!")
    class_type = data["type"]
    amount = data["amount"]
    class_idx = data["class_idx"]
    compare = data['compare']

    class_idx2 = data["class_idx2"]

    existend2 = False
    existend_imgs2 = False
    title2 = False
    artist2 = False
    year2 = False
    encoded_img2 = False
    image_list2 = False

    # Load a placeholder image.
    # TODO: Obtain a generated image here.
    image_list, image, title, artist, year = get_image(class_idx, class_type)
    # path = os.path.join(os.path.dirname(__file__), image_file)
    # image = Image.open(urllib3.urlopen(image))
    image = Image.open(urllib.request.urlopen(image))
    # Encode the image for the response.
    img_stream = BytesIO()
    image.save(img_stream, format="png")
    encoded_img = encodebytes(img_stream.getvalue()).decode('ascii')
    


    if compare:
        image_list2, image2, title2, artist2, year2 = get_image(class_idx2, class_type)
        image2 = Image.open(urllib.request.urlopen(image2))
        # Encode the image for the response.
        img_stream2 = BytesIO()
        image2.save(img_stream2, format="png")
        encoded_img2 = encodebytes(img_stream2.getvalue()).decode('ascii')
        
    socketio.emit("set_image", {
            "existend": f"data:image/png;base64, {encoded_img}",
            "existend_imgs": image_list,
            "title": title,
            "artist": artist,
            "year": year,
            "existend2": f"data:image/png;base64, {encoded_img2}",
            "existend_imgs2": image_list2,
            "title2": title2,
            "artist2": artist2,
            "year2": year2
        })


    # Get the primary color of the image.
    colors, percentages, dom_color = detect_colors(image)
    socketio.emit("change_color", dom_color)
    

    '''
    socketio.emit("set_color_pie", {
        "colors": colors,
        "percentages": percentages,
    })
    '''

    # model_data = get_model_data()

    dictionary = retrieve_info(class_idx)
    dictionary2 = False
    if compare:
        colors2, percentages2, dom_color2 = detect_colors(image2)
        dictionary2 = retrieve_info(class_idx2)

    if compare:
        socketio.emit("get_summary", {
            "summary": dictionary['summary'],
            "related_terms": dictionary['related_terms'],
            "summary2": dictionary2['summary'],
            "related_terms2": dictionary2['related_terms']
        })
    else:
        socketio.emit("get_summary", {
            "summary": dictionary['summary'],
            "related_terms": dictionary['related_terms'],
            "summary2": dictionary2,
            "related_terms2": dictionary2
        })

    # socketio.emit("set_selected_artist", {
    #     "artist_options": get_artists(model_data),
    # })

    '''
    histograms = get_artist_histograms()
    socketio.emit("get_style_hists", {
        "series": [{
            "values": values,
            "text": key,
        } for key, values in histograms.items()],
    })
    '''


@socketio.event
def generate_images(data):
    if not torch.cuda.is_available():
        socketio.emit("images_generated", {
            "images": [],
            "images2": [],
            "seeds": [],
            "success": False,
            "message": "No Graphical Processing Unit available!"
        })
        return

    classification_type = data["type"]
    amount = data["amount"]
    class_idx = data["class_idx"]
    compare = data['compare']
    images2 = false
    if compare:
        class_idx2 = data["class_idx2"]

    seeds = np.random.randint(0, 10000, amount)

    if classification_type == "artists":
        try:
            class_idx = generate.ARTIST_LABELS.index(class_idx)
            if compare:
                class_idx2 = generate.ARTIST_LABELS.index(class_idx2)
        except ValueError:
            message = f"Label {repr(class_idx)} does not exist!"
            socketio.emit("images_generated", {
                "images": [],
                "seeds": [],
                "success": False,
                "message": message,
            })
            raise ValueError(message)

        images = generate.generate_images(G_artists, seeds, class_idx)
        if compare:
            images2 = generate.generate_images(G_artists, seeds, class_idx2)
    elif classification_type == "centuries":
        print(f"Generating painting from the {class_idx}th century")
        images = generate.generate_images(G_centuries, seeds, class_idx)
        if compare:
            images2 = generate.generate_images(G_centuries, seeds, class_idx2)
    else:
        message = f"Type {repr(classification_type)} is not known!"
        socketio.emit("images_generated", {
            "images": [],
            "seeds": [],
            "success": False,
            "message": message
        })
        raise ValueError(message)

    image_data = []
    image_data2 = []

    for image in images:
        colors, percentages, dom_color = detect_colors(image)

        image_data.append({
            'image': encode_image(image),
            'dominant_color': dom_color,
            'color_palette': colors,
            'color_distribution': percentages,
        })

    first_image = image_data[0]
    socketio.emit("change_color", first_image['dominant_color'])
    socketio.emit("set_color_pie", {
        "colors": first_image['color_palette'],
        "percentages": first_image['color_distribution'],
    })


    if compare:
        for image in images2:
            colors2, percentages2, dom_color2 = detect_colors(image2)

            image_data2.append({
                'image': encode_image(image2),
                'dominant_color': dom_color2,
                'color_palette': colors2,
                'color_distribution': percentages2,
            })

        first_image2 = image_data2[0]
        # socketio.emit("change_color", first_image2['dominant_color'])
        socketio.emit("set_color_pie2", {
            "colors": first_image2['color_palette'],
            "percentages": first_image2['color_distribution'],
        })



    socketio.emit("images_generated", {
        "images": image_data,
        "images2": image_data2,
        "seeds": seeds.tolist(),
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
    artists = data['artists']
    histograms = _get_artist_histograms(model_data, artists)
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
