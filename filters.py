from .config import BASE_JSON
from backend.settings import es
from .utils import DATETIME_FORMAT
import datetime
import json
from .clustering import flatten_string


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


def getESQueryFromFilter(filter):

    # if filter['selectedFilter'] == '':
    #     raise ParseFilterExcpetion
    # if filter['selectedFilter']['value'] == 'allFollowers':
    #     # query["query"] = {
    #     #     "match_all": {}
    #     # }
    #     pass
    if filter['selectedFilter']['value'] == 'twitterHandle':
        return {
            "term": {"screen_name": filter['twitterHandle']}
        }
    elif filter['selectedFilter']['value'] == 'followerCount':
        if filter['followerCountCondition']['value'] == 'isGreaterThan':
            return {
                "range": {"followers_count": {"gte": filter['followerCount']}}
            }
        elif filter['followerCountCondition']['value'] == 'isLessThan':
            return {
                "range": {"followers_count": {"lte": filter['followerCount']}}
            }
        else:
            return {
                "range": {"followers_count": {"gte": filter['followerCount'], "lte": filter['followerCount1']}}
            }
    elif filter['selectedFilter']['value'] == 'friendCount':
        if filter['friendCountCondition']['value'] == 'isGreaterThan':
            return {
                "range": {"friends_count": {"gte": filter['friendCount']}}
            }
        elif filter['friendCountCondition']['value'] == 'isLessThan':
            return {
                "range": {"friends_count": {"lte": filter['friendCount']}}
            }
        else:
            return {
                "range": {"friends_count": {"gte": filter['friendCount'], "lte": filter['friendCount1']}}
            }
    elif filter['selectedFilter']['value'] == 'topics':
        topics = filter['topics']
        if filter['topicsCondition']['value'] == 'or':
            return {
                "query_string": {
                    "fields": [
                        "description",
                        "status.text"
                    ],
                    "query": ' OR '.join(map(str, topics))
                }}
        else:
            return {
                "query_string": {
                    "fields": [
                        "description",
                        "status.text"
                    ],
                    "query": ' AND '.join(map(str, topics))
                }}
    elif filter['selectedFilter']['value'] == 'lastSeen':
        if filter['lastSeenCondition']['value'] == 'isGreaterThan':
            return {
                "range": {"status.created_at": {"gte": filter['startDate']}}
            }
        elif filter['lastSeenCondition']['value'] == 'isLessThan':
            return {
                "range": {"status.created_at": {"lte": filter['startDate']}}
            }
        else:
            return {
                "range": {"status.created_at": {"gte": filter['startDate'], "lte": filter['endDate']}}
            }
    elif filter['selectedFilter']['value'] == 'country':
        return {
            "term": {"country": filter['selectedCountry']['value']}
        }
        pass
    elif filter['selectedFilter']['value'] == 'flag':
        if filter['flagCondition']['value'] == 'is':
            return {
                "term": {filter['flagOption']['value']: True}
            }
        else:
            return {
                "term": {filter['flagOption']['value']: False}
            }
    else:
        raise ParseFilterExcpetion


default_source_fields = ["id_str", "name", "screen_name", "location", "description", "url", "followers_count", "friends_count", "created_at",
                         "verified", "statuses_count", "favourites_count", "status.created_at", "profile_image_url_https", "muting", "blocking", "follow_order", "escher_account"]


def getESQueryFromFilters(filters, escher_account_id_str, size, source_fields=default_source_fields):

    empty_filters = list(filter(lambda x: x['selectedFilter'] == '', filters))
    if len(empty_filters) > 0:
        raise ParseFilterExcpetion

    all_followers_filters = list(
        filter(lambda x: x['selectedFilter']['value'] == 'allFollowers', filters))
    if len(filters) > 1 and len(all_followers_filters) > 0:
        raise ParseFilterExcpetion

    must = [{"term": {"escher_account": escher_account_id_str}},
            {"exists": {"field": "profile_image_url_https"}}]

    # source_fields = ["id_str", "name", "screen_name", "location", "description", "url", "followers_count", "friends_count", "created_at",
    #                  "verified", "statuses_count", "favourites_count", "status.created_at", "profile_image_url", "muting", "blocking", "follow_order", "escher_account"]
    query = {
        "_source": source_fields,
        "size": size,
        "sort": [  # to get latest followers on top
            {
                "follow_order": {
                    "order": "desc"
                }
            }
        ]
    }
    if len(all_followers_filters) > 0:
        # must will have the escher_account and must_not will only return users
        # that have the profile data in them
        query["query"] = {
            "bool": {
                "must": must
            }
        }
        return query
    else:
        must_queries = list(map(lambda x: getESQueryFromFilter(x), filters))
        # must will have all the filters, and must_not will make sure
        # users without data will not be returned
        query["query"] = {
            "bool": {
                "must": must_queries + must
            }
        }
        return query
    pass


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
