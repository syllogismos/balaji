
import pickle
from config import FOLLOWER_PKL



def get_followers_local():
  try:
    followers = pickle.load(open(FOLLOWER_PKL, 'rb'))
  except:
    print("local db doesn't exist or is corrupted\nupdating the local follower data")
    followers = update_followers_db(api)
  return followers