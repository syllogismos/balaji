
import pickle
import json
from .config import FOLLOWER_PKL, BASE_JSON
import datetime


def get_followers_local():
    try:
        followers = pickle.load(open(FOLLOWER_PKL, 'rb'))
    except:
        print("local db doesn't exist or is corrupted\nuse the --populate flag to populate your local db")
        followers = []
    return followers


def get_followers_from_json():
    try:
        followers = json.load(open(BASE_JSON, 'rb'))
    except:
        followers = []
    return followers


DATETIME_FORMAT = '%a %b %d %H:%M:%S +0000 %Y'


def python_date(x): return datetime.datetime.strptime(x, DATETIME_FORMAT)


def get_upsert_commands(me, follower_tup, index):
    follower, follow_order = follower_tup
    _id = me.id_str + "a" + follower.id_str
    js = follower._json
    js['escher_account'] = me.id_str
    js['follow_order'] = follow_order
    js['created_at'] = python_date(js['created_at'])
    if 'status' in js:
        js['status']['created_at'] = python_date(js['status']['created_at'])
    return [{'update': {'_index': index, '_id': _id}}, {'doc': js,
                                                        'doc_as_upsert': True}]


def get_bulk_commands(me, followers, index):
    bulk_commands = []
    for follower in followers:
        b = get_upsert_commands(me, follower, index)
        bulk_commands.extend(b)
    return bulk_commands
# Timezone Finder
# import datetime
# import pytz
# from tzwhere import tzwhere

# tzwhere = tzwhere.tzwhere()
# timezone_str = tzwhere.tzNameAt(37.3880961, -5.9823299) # Seville coordinates
# timezone_str
# #> Europe/Madrid

# timezone = pytz.timezone(timezone_str)
# dt = datetime.datetime.now()
# timezone.utcoffset(dt)
# #> datetime.timedelta(0, 7200)
