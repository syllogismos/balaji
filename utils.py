
import pickle, json
from config import FOLLOWER_PKL, BASE_JSON



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



## Timezone Finder
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