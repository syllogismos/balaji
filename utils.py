
import pickle
from config import FOLLOWER_PKL



def get_followers_local():
  try:
    followers = pickle.load(open(FOLLOWER_PKL, 'rb'))
  except:
    print("local db doesn't exist or is corrupted\nupdating the local follower data")
    followers = update_followers_db(api)
  return followers



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