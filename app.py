import requests
from flask import Flask, render_template
from polyline_decoder import decode_polyline
from constants import DIRECTION_API, API_KEY, APP_CONFIG_SECRET_KEY
from forms import InputForm
import haversine as hs
from haversine import Unit
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config['SECRET_KEY'] = APP_CONFIG_SECRET_KEY
Bootstrap(app)


def get_direction_data(origin, destination, mode="driving"):
    """
    Frames the API URL, adds the required params and does a GET call to get the appropriate response.

    @params: origin -> str - LatLang co-ordinates of source formatted as "LAT,LANG" co-ordinate as string.
            destination -> str - LatLang co-ordinates of destination formatted as "LAT,LANG" co-ordinate as string.
            mode -> str - API supports 4 kind of modes (Driving, Walking, Transiting, etc.) Default value 'driving'
    @returns: response -> JSON - API response of direction API based upon the URL and the params passed to it.s
    """
    api_params = {
        'key': API_KEY,
        'origin': origin,
        'destination': destination,
        'mode': mode
    }
    r = requests.get(DIRECTION_API, params=api_params)
    print(r.url)
    return r.json()


def get_polyline_points(steps):
    """
    Extracts polyline points from each step from the API response and maintains it in a list.

    @params: steps -> List<steps> - list of all the steps present in each route from source to destination.
    @returns: polyline_list -> List<str> - list of polylines points stored sequentially w.r.t. steps of each route.
    """
    polyline_list = []
    for step in steps:
        point = step['polyline']['points']
        polyline_list.append(point)

    return polyline_list


def get_distance(coordinates_list, distance_gap=50):
    """
    Calculates cumulative distance of each adjacent co-ordinates.
    If the distance is equal to or more than the offset, the respective co-ordinates is appended to final list.
    If the distance is less, then the cumulative distance to next co-ordinate is checked util sums closer to offset.

    @params: coordinates_list -> List<Tuple<float, float>> - List of all the LatLang co-ordinates created by decoding
                                                             the polylines points.
             distance_gap -> int - Expected approximate gap between two adjacent co-ordinates in final result.
    @returns: result -> List<Tuple<float, float>> - List of co-ordinates at a distance equal to distance_gap, along the
                                                    route from source to destination.
    """
    result = []
    current_index = 0
    next_index = 1
    rem = 0
    result.append(coordinates_list[current_index])
    length = len(coordinates_list)

    while next_index < length:
        distance = hs.haversine(coordinates_list[current_index], coordinates_list[next_index], unit=Unit.METERS)
        if rem <= 0:
            rem = distance_gap
        rem = rem - distance
        if rem <= 0:
            result.append(coordinates_list[next_index])
            current_index = next_index
            next_index = current_index + 1
        elif rem > 0:
            current_index = next_index
            next_index = current_index + 1

    return result


def get_coordinates_from_polylines(polylines_list):
    """
    Creates a list of LatLang co-ordinates after decoding all the polylines points of each step in the route
    sequentially.

    @params: polylines_list -> List<str> - List of polyline points of each step filtered from the direction API
                                           response.
    @returns: lat_lang_coordinates -> List<Tuple<float, float>> - List of LatLang co-ordinates decoded from the
                                                                  polylines points.
    """
    lat_lang_coordinates = []
    for polyline in polylines_list:
        coordinates = decode_polyline(polyline)
        lat_lang_coordinates.extend(coordinates)

    return lat_lang_coordinates


@app.route("/", methods=['GET', 'POST'])
def index():
    """
    Application's entry point.
    """
    coordinates = []
    result = []
    form = InputForm()
    if form.validate_on_submit():
        result = []
        coordinates = []
        source_lngs = form.src_long.data
        source_lats = form.src_lat.data
        dest_lngs = form.dest_long.data
        dest_lats = form.dest_lat.data
        offset = form.offset.data

        origin = str(source_lats) + ',' + str(source_lngs)
        destination = str(dest_lats) + ',' + str(dest_lngs)

        response = get_direction_data(origin=origin, destination=destination)
        steps = response['routes'][0]['legs'][0]['steps']
        polylines = get_polyline_points(steps)
        coordinates = get_coordinates_from_polylines(polylines)
        result = get_distance(coordinates, distance_gap=int(offset))
        print(polylines)

    return render_template('index.html', form=form, coordinates=result)
