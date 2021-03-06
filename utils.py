
import pickle
import json
from .config import FOLLOWER_PKL, BASE_JSON, my_keys
import datetime
import tweepy
import requests
import traceback
from backend.settings import ses_email_client


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


def get_upsert_commands_user_deets(me, follower, index):
    _id = me.id_str + "a" + follower.id_str
    js = follower._json
    js['escher_account'] = me.id_str
    js['created_at'] = python_date(js['created_at'])
    if 'status' in js:
        js['status']['created_at'] = python_date(js['status']['created_at'])
    return [{'update': {'_index': index, '_id': _id}}, {'doc': js,
                                                        'doc_as_upsert': True}]


def get_bulk_commands_user_deets(me, followers, index):
    bulk_commands = []
    for follower in followers:
        b = get_upsert_commands_user_deets(me, follower, index)
        bulk_commands.extend(b)
    return bulk_commands


def get_upsert_commands_follower_id(me, follower_id_tup, index):
    follow_id, follow_order = follower_id_tup
    _id = me.id_str + 'a' + str(follow_id)
    js = {}
    js['escher_account'] = me.id_str
    js['follow_order'] = follow_order
    js['id_str'] = str(follow_id)
    return [{'update': {'_index': index, '_id': _id}}, {'doc': js, 'doc_as_upsert': True}]


def get_bulk_commands_follower_ids(me, ids, index):
    bulk_commands = []
    for follower_id in ids:
        b = get_upsert_commands_follower_id(me, follower_id, index)
        bulk_commands.extend(b)
    return bulk_commands


def create_api_user_access_tokens(userDetails):
    auth = tweepy.OAuthHandler(my_keys['api_key'], my_keys['api_secret'])
    if 'twitterUser' in userDetails:
        credential = userDetails['twitterUser']['credential']
        auth.set_access_token(
            credential['oauthAccessToken'], credential['oauthTokenSecret'])
    api = tweepy.API(auth)
    return api


def send_email_alert(subject, body):
    try:
        response = ses_email_client.send_email(
            Source='anil@eschernode.com',
            Destination={
                'ToAddresses': [
                    'anil@eschernode.com',
                ],
            },
            Message={
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': body,
                        'Charset': 'UTF-8'
                    }
                }
            },
            ReplyToAddresses=[
                'anil@eschernode.com',
            ]
        )
        print(response)
    except Exception as e:
        print("Exception while sending sparkpost email")
        traceback.print_exc()


class DynamicLinks:
    FIREBASE_API_URL = 'https://firebasedynamiclinks.googleapis.com/v1/shortLinks?key={}'

    def __init__(self, api_key, domain, timeout=10):
        self.api_key = api_key
        self.domain = domain
        self.timeout = timeout
        self.api_url = self.FIREBASE_API_URL.format(self.api_key)

    def generate_dynamic_link(self, link, short=True, params={}):
        payload = {
            "dynamicLinkInfo": {
                "domainUriPrefix": self.domain,
                "link": link
            },
            "suffix": {
                "option": "SHORT" if short else "UNGUESSABLE"
            }
        }
        payload['dynamicLinkInfo'].update(params)

        response = requests.post(
            self.api_url, json=payload, timeout=self.timeout)

        data = response.json()

        if not response.ok:
            raise FirebaseDynamicLinksError(data)

        return data['shortLink']


class FirebaseDynamicLinksError(Exception):
    pass

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

# OR is spelled should
# AND is spelled must
# NOR is spelled should_not


# Sample User
# """
# {
#         "_index" : "followers_anil",
#         "_type" : "_doc",
#         "_id" : "2360845790a342167747",
#         "_score" : 1.0,
#         "_source" : {
#           "id" : 342167747,
#           "id_str" : "342167747",
#           "name" : "Debadeepta Dey",
#           "screen_name" : "debadeepta",
#           "location" : "Redmond, WA",
#           "description" : "Principal Researcher @ Microsoft Research AI. Robotics, Reinforcement Learning, Control, Vision and Autonomous Vehicles.",
#           "url" : "https://t.co/fh3fyvx1tI",
#           "entities" : {
#             "url" : {
#               "urls" : [
#                 {
#                   "url" : "https://t.co/fh3fyvx1tI",
#                   "expanded_url" : "http://www.debadeepta.com/",
#                   "display_url" : "debadeepta.com",
#                   "indices" : [
#                     0,
#                     23
#                   ]
#                 }
#               ]
#             },
#             "description" : {
#               "urls" : [ ]
#             }
#           },
#           "protected" : false,
#           "followers_count" : 1071,
#           "friends_count" : 1202,
#           "listed_count" : 11,
#           "created_at" : "2011-07-25T15:56:59",
#           "favourites_count" : 3807,
#           "utc_offset" : null,
#           "time_zone" : null,
#           "geo_enabled" : false,
#           "verified" : false,
#           "statuses_count" : 443,
#           "lang" : null,
#           "status" : {
#             "created_at" : "2020-06-24T03:11:36",
#             "id" : 1275627608462356483,
#             "id_str" : "1275627608462356483",
#             "text" : "@geomblog height = K - value",
#             "truncated" : false,
#             "entities" : {
#               "hashtags" : [ ],
#               "symbols" : [ ],
#               "user_mentions" : [
#                 {
#                   "screen_name" : "geomblog",
#                   "name" : "Suresh Venkatasubramanian",
#                   "id" : 1368571,
#                   "id_str" : "1368571",
#                   "indices" : [
#                     0,
#                     9
#                   ]
#                 }
#               ],
#               "urls" : [ ]
#             },
#             "source" : """ < a href = "https://mobile.twitter.com" rel = "nofollow" > Twitter Web App < /a > """,
#             "in_reply_to_status_id" : 1275537409518624768,
#             "in_reply_to_status_id_str" : "1275537409518624768",
#             "in_reply_to_user_id" : 1368571,
#             "in_reply_to_user_id_str" : "1368571",
#             "in_reply_to_screen_name" : "geomblog",
#             "geo" : null,
#             "coordinates" : null,
#             "place" : null,
#             "contributors" : null,
#             "is_quote_status" : false,
#             "retweet_count" : 0,
#             "favorite_count" : 1,
#             "favorited" : false,
#             "retweeted" : false,
#             "lang" : "en"
#           },
#           "contributors_enabled" : false,
#           "is_translator" : false,
#           "is_translation_enabled" : false,
#           "profile_background_color" : "000000",
#           "profile_background_image_url" : "http://abs.twimg.com/images/themes/theme1/bg.png",
#           "profile_background_image_url_https" : "https://abs.twimg.com/images/themes/theme1/bg.png",
#           "profile_background_tile" : false,
#           "profile_image_url" : "http://pbs.twimg.com/profile_images/590174349677703168/A8682S-s_normal.jpg",
#           "profile_image_url_https" : "https://pbs.twimg.com/profile_images/590174349677703168/A8682S-s_normal.jpg",
#           "profile_banner_url" : "https://pbs.twimg.com/profile_banners/342167747/1466110413",
#           "profile_link_color" : "E81C4F",
#           "profile_sidebar_border_color" : "000000",
#           "profile_sidebar_fill_color" : "000000",
#           "profile_text_color" : "000000",
#           "profile_use_background_image" : false,
#           "has_extended_profile" : false,
#           "default_profile" : false,
#           "default_profile_image" : false,
#           "following" : true,
#           "live_following" : false,
#           "follow_request_sent" : false,
#           "notifications" : false,
#           "muting" : false,
#           "blocking" : false,
#           "blocked_by" : false,
#           "translator_type" : "none",
#           "escher_account" : "2360845790",
#           "follow_order" : 65
#         }
#       },
# """
