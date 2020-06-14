from config import BASE_JSON
from utils import DATETIME_FORMAT
import datetime, json


def get_followers_from_json():
  followers = json.load(open(BASE_JSON, 'rb'))
  return followers

def country_code_filter(followers, code):
  return list(filter(lambda x: x['country_code'] == code, followers))
  
def is_within_daterange(f, days):
  python_date = lambda x: datetime.datetime.strptime(x, DATETIME_FORMAT)
  last_seen = python_date(f['last_seen']) if f['last_seen'] != '' else python_date(f['created_at'])
  days_delta = datetime.datetime.today() - last_seen
  return days_delta.days < days

def lastseen_filter(followers, days):
  return list(filter(lambda f: is_within_daterange(f, days), followers))
  
  

