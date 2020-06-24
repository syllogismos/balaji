from config import BASE_JSON
from utils import DATETIME_FORMAT
import datetime
import json
from clustering import flatten_string


class ParseFilterExcpetion(Exception):
    """Exception when parsing the filter fails"""
    pass


filterInitialState = {
    'id': '',
    'selectedFilter': '',
    'twitterHandle': '',
    'selectedCountry': '',
    'followerCount': 0,
    'followerCount1': 0,
    'friendCount': 0,
    'frinedCount1': 0,
    'topicsCondition': {
        'label': 'AND',
        'value': 'and',
        'key': 0,
    },
    'twitterStringCondition': {
        'label': 'Is',
        'value': 'is',
        'key': 0,
    },
    'selectedNumberCondition': {
        'label': 'Is Greater Than',
        'value': 'isGreaterThan',
        'key': 0,
    },
    'followerCountCondition': {
        'label': 'Is Greater Than',
        'value': 'isGreaterThan',
        'key': 0,
    },
    'lastSeenCondition': {
        'label': 'Is Greater Than',
        'value': 'isGreaterThan',
        'key': 0,
    },
    'friendCountCondition': {
        'label': 'Is Greater Than',
        'value': 'isGreaterThan',
        'key': 0,
    },
    # 'startDate': new Date(),
    # 'endDate': new Date(),
    'topics': [],
}


def getUsersFromFilter(filter):
    if filter['selectedFilter'] == '':
        raise ParseFilterExcpetion
    if filter['selectedFilter']['value'] == 'allFollowers':
        pass
    elif filter['selectedFilter']['value'] == 'twitterHandle':
        pass
    elif filter['selectedFilter']['value'] == 'followerCount':
        pass
    elif filter['selectedFilter']['value'] == 'friendCound':
        pass
    elif filter['selectedFilter']['value'] == 'topics':
        pass
    elif filter['selectedFilter']['value'] == 'lastSeen':
        pass
    elif filter['selectedFilter']['value'] == 'country':
        pass
    else:
        raise ParseFilterExcpetion


def getUsersFromFilters(filters):


def country_code_filter(followers, code):
    return list(filter(lambda x: x['country_code'] == code, followers))


def is_within_daterange(f, days):
    def python_date(x): return datetime.datetime.strptime(x, DATETIME_FORMAT)
    last_seen = python_date(
        f['last_seen']) if f['last_seen'] != '' else python_date(f['created_at'])
    days_delta = datetime.datetime.today() - last_seen
    return days_delta.days < days


def lastseen_filter(followers, days):
    return list(filter(lambda f: is_within_daterange(f, days), followers))


def top_n_filter(followers, limit=10):
    followers.sort(key=lambda x: x['followers_count'], reverse=True)
    return followers[:limit]


def token_filter(followers, token):
    # print(token)
    if '+' in token and ',' in token:
        raise Exception
    if '+' in token or ',' in token:
        if '+' in token:
            plustokens = list(
                map(lambda x: flatten_string(x), token.split('+')))
            followers = list(filter(lambda f: all(
                map(lambda x: x in f['tokens'], plustokens)), followers))
        else:
            commatokens = list(
                map(lambda x: flatten_string(x), token.split(',')))
            followers = list(filter(lambda f: any(
                map(lambda x: x in f['tokens'], commatokens)), followers))
    else:
        token = flatten_string(token)
        followers = list(filter(lambda f: token in f['tokens'], followers))
    return followers
