from .utils import get_followers_local
from .config import BASE_CSV, BASE_JSON
import json
from geopy.geocoders import Nominatim
from .clustering import get_tokens


def get_country_from_location(location):
    locator = Nominatim(user_agent="targetted twitter DM bot")
    location = locator.geocode(location)
    if location:
        detailed_location = locator.reverse(location._point)
        country_code = detailed_location._raw['address']['country_code']
    else:
        country_code = ''
    return country_code


def build_base_json():
    # TODO figure out a work around for ratelimiting from geocoding while figuring out the country code
    followers = get_followers_local()
    def json_getter_1(f, c): return f._json[c] if c in f._json else ''

    def json_getter_2(
        follower, col, attr): return f._json[col][attr] if col in f._json else ''

    def cols_getter(f): return {
        'id': str(json_getter_1(f, 'id')),
        'name': str(json_getter_1(f, 'name')),
        'screen_name': str(json_getter_1(f, 'screen_name')),
        'location': str(json_getter_1(f, 'location')),
        'followers_count': str(json_getter_1(f, 'followers_count')),
        'created_at': str(json_getter_1(f, 'created_at')),
        'time_zone': str(json_getter_1(f, 'time_zone')),
        'last_seen': str(json_getter_2(f, 'status', 'created_at')),
        'country_code': get_country_from_location(json_getter_1(f, 'location')),
        'tokens': get_tokens(f)[1]
    }
    with open(BASE_JSON, 'w') as jsonfile:
        lines = []
        for f in followers:
            line = cols_getter(f)
            lines.append(line)
        json.dump(lines, jsonfile)
