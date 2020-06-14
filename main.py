import tweepy
from tqdm import tqdm
import pickle
from config import create_api

import argparse


FOLLOWER_DIR = "MY_FOLLOWERS.pkl"

def update_followers_db(api):
  followers = []
  try:
    for follower in tqdm(get_limit_handled(tweepy.Cursor(api.followers).items())):
      followers.append(follower)
  except:
    print("Exception while traversing through followers cursor")
    pass

  print('No of followers downloaded', len(followers))    
  print('updating local followers db')
  pickle.dump(followers, open(FOLLOWER_DIR, 'wb'))
  return followers

def get_followers_local():
  try:
    followers = pickle.load(open(FOLLOWER_DIR, 'rb'))
  except:
    print("local db doesn't exist or is corrupted\nupdating the local follower data")
    followers = update_followers_db(api)
  return followers

def get_top_followers(followers, limit=10, criterion=None):
  """
  Get top users with a given criterion, if none, return sorted users with most followers
  """
  followers.sort(key=lambda x: x._json['followers_count'], reverse=True)
  return followers[:limit]

# Get followers rate limit cursor
def get_limit_handled(cursor):
  while True:
    try:
      yield cursor.next()
    except tweepy.RateLimitError:
      time.sleep(15*60)


def send_dm(followers, message):
  for follower in tqdm(followers):
    try:
      api.send_direct_message(follower.id, message)
    except:
      print("sending message failed")
  print('No of people I sent this message to: ', len(followers))


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='DM your followers')
  parser.add_argument('limit', type=int, nargs='?', default=10, help='DM criterion limit')
  parser.add_argument('--update', action="store_true", help="Update follower db locally")
  parser.add_argument('--forreals', action='store_true', help='Send DMs forreals')
  args = parser.parse_args()
  api = create_api()
  if args.update:
    followers = update_followers_db(api)
  if not args.update:
    followers = get_followers_local()
  top = get_top_followers(followers, limit=args.limit)
  message = input('Type your DM Here: ')
  print('This is your DM: ', message)
  if args.forreals:
    print("You are sending the message for reals do your want to continue?")
    final_confirmation = input('Y/N --> ')
    if final_confirmation == 'Y':
      send_dm(top, message)
  else:
    print('You did a dryrun to send',
      args.limit,
      'people the following message\n',
      message,
      '\nUse the flag --forreals to send the message for reals')