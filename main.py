import tweepy
from tqdm import tqdm
import pickle, time
from config import create_api, FOLLOWER_PKL
from utils import get_followers_local, get_followers_from_json
from filters import country_code_filter, lastseen_filter, top_n_filter
from preprocess import build_base_json

import argparse

# TODO Partial db update, and handle full db update
# DONE seperate db update, and send dms in cmd tool
# DONE refactor cmd tool args
# DONE figure out filters mechanism
# DONE last_seen filter, obviously not reliable if you cant/dont update the db regularly
# DONE country filter
# TODO clustering followers
# TODO get most relevant followers
# TODO send at a particular time based on timezone, time 1-24
# TODO checks to make sure u dont send a dm to the same person in a day thru this
# TODO Refactor



def update_followers_db(api):
  followers = []
  try:
    for follower in tqdm(get_limit_handled(tweepy.Cursor(api.followers, count=200).items())):
      followers.append(follower)
  except:
    print("Exception while traversing through followers cursor")
    pass

  print('No of followers downloaded', len(followers))    
  print('updating local followers db')
  pickle.dump(followers, open(FOLLOWER_PKL, 'wb'))
  return followers

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
      api.send_direct_message(follower['id'], message)
    except:
      print("sending message failed")
  print('No of people I sent this message to: ', len(followers))


if __name__ == '__main__':

  description = """
FILTER YOUR FOLLOWERS AND DM THEM IN BULK

Example Usage

Populate your follower database locally like below
`python main.py --populate`
Ideally you wont do this very often, maybe monthly once


Use the dm flag and additional filters to filter your users
and direct message them
To DM the top 10 followers who has the most no of followers
`python main.py --dm`

To DM the top 1000 followers who has the most no of followers
`python main.py --dm --limit 1000`

To DM all the users who are from US, active in the last 30 days 
and the top 100 users with the most no of followers
`python main.py --dm --cc us --days 30 --limit 100`
  """
  parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawDescriptionHelpFormatter)
  
  # Arguments for updating your local follower db and further processing
  parser.add_argument('--populate', action="store_true", help="Update follower db locally")
  parser.add_argument('--partial', action="store_true", help="If you already had your local db, and want to update it")
  

  # Arguments for filtering your followers and sending dms if you want
  parser.add_argument('--dm', action="store_true", help="Send DM's, you run this after you update your follower db locally")
  parser.add_argument('--forreals', action="store_true", help="Only when you add forreals flag you will send dms")
  parser.add_argument('--cc', type=str, default="", help="Filter your followers based on country code")
  parser.add_argument('--days', type=int, default=0, help="Get followers who are active within the last n number of days")
  parser.add_argument('--limit', type=int, default=10, help="Get the top n followers who have the most no of followers")
  args = parser.parse_args()

  if args.populate and args.dm:
    print("You can't update follower database and send DMs at the same time\nUpdate followers locally and then run the command with flag dm")
  api = create_api()
  if args.populate:
    # update db
    print("Downloading your follower data")
    me = api.me()
    followers_count = me.followers_count
    time_in_hours = followers_count / (15 * 200 * 4)
    print("Estimated time for the download to complete based on twitter api rate limits is %f hours" %(time_in_hours))
    followers = update_followers_db(api)
    print("Preprocessing the downloaded follower data, it will take some time too to populate fields like country, timezone, and clusters")
    build_base_json()
    pass

  elif args.dm:
    # apply filters and send dms
    followers_json = get_followers_from_json()
    print('Total no of followers you have locally are', len(followers_json))
    if args.cc != '':
      followers_json = country_code_filter(followers_json, args.cc)
      print('Total no of followers who are from the country %s are %d' % (args.cc, len(followers_json)))
    if args.days != 0:
      followers_json = lastseen_filter(followers_json, args.days)
      print('Total no of followers who are last seen within %d days are %d' %(args.days, len(followers_json)))
    followers_json = top_n_filter(followers_json, args.limit)
    
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
    print("No of followers after all the filtering is done is %d" %len(followers_json))
  
    message = input('Type your DM Here: ')
    print('This is your DM: %s' %message)


    if args.forreals:
      # Send DM's for reals.
      print("You are sending the DM's for reals do you want to continue?")
      final_confirmation = input('Y/N --> ')
      if final_confirmation == 'Y':
        send_dm(followers_json, message)
        pass
    else:
      print("""You did a dry run to send %d of your followers the following message\n%s\n
Use the flag --forreals to send the message for reals""" %(len(followers_json), message))
