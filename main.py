import tweepy
from tqdm import tqdm
import pickle
from config import create_api

import argparse


follower_directory = "MY_FOLLOWERS.pkl"






def update_followers_db(api):
  followers = []
  try:
    for follower in tqdm(tweepy.Cursor(api.followers).items()):
      followers.append(follower)
  except:
    print("Exception while traversing through followers cursor")
    pass

  print('No of followers downloaded', len(followers))    
  print('updating local followers db')
  pickle.dump(followers, open(follower_directory, 'wb'))
  return followers

  
def get_top_followers(followers, limit=10, criterion=None):
  """
  Get top users with a given criterion, if none, return users with most followers
  """
  followers.sort(key=lambda x: x._json['followers_count'], reverse=True)
  return followers[:limit]


# Rate limiting example with custom cursor
# # In this example, the handler is time.sleep(15 * 60),
# # but you can of course handle it in any way you want.

# def limit_handled(cursor):
#     while True:
#         try:
#             yield cursor.next()
#         except tweepy.RateLimitError:
#             time.sleep(15 * 60)

# for follower in limit_handled(tweepy.Cursor(api.followers).items()):
#     if follower.friends_count < 300:
#         print(follower.screen_name)

def send_dm(followers, message):
  for follower in tqdm(followers):
    api.send_direct_message(follower.id, message)
  print('No of people I sent this message to: ', len(followers))


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='DM your followers')
  parser.add_argument('limit', type=int, help='A required integer positional argument')
  args = parser.parse_args()
  api = create_api()
  followers = update_followers_db(api)
  top = get_top_followers(followers)
  message = input('Type your DM Here: ')
  print('This is your DM: ', message)
  send_dm(top, message)