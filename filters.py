from config import BASE_JSON
from utils import DATETIME_FORMAT
import datetime, json
from clustering import flatten_string


def country_code_filter(followers, code):
  return list(filter(lambda x: x['country_code'] == code, followers))
  
def is_within_daterange(f, days):
  python_date = lambda x: datetime.datetime.strptime(x, DATETIME_FORMAT)
  last_seen = python_date(f['last_seen']) if f['last_seen'] != '' else python_date(f['created_at'])
  days_delta = datetime.datetime.today() - last_seen
  return days_delta.days < days

def lastseen_filter(followers, days):
  return list(filter(lambda f: is_within_daterange(f, days), followers))

def top_n_filter(followers, limit=10):
  followers.sort(key=lambda x: x['followers_count'], reverse=True)
  return followers[:limit]
  
def token_filter(followers, token):
  token = flatten_string(token)
  return list(filter(lambda f: token in f['tokens'], followers))

  

