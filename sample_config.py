import tweepy

def create_api():
  # consumer_key, consumer_secret
  auth = tweepy.OAuthHandler('CONSUMER_KEY', 'CONSUMER_SECRET')
  # access token, access token secret
  auth.set_access_token('ACCESS_KEY', 'ACCESS_SECRET')

  api = tweepy.API(auth)
  return api