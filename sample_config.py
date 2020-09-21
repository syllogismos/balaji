import tweepy
import elasticsearch

FOLLOWER_PKL = "MY_FOLLOWERS.pkl"
BASE_CSV = "FOLLOWERS.csv"
BASE_JSON = "FOLLOWERS.json"

my_keys = {'api_key': '',
           'api_secret': '',
           'access_token': '',
           'access_token_secret': ''
           }


def create_api():
    # consumer_key, consumer_secret
    auth = tweepy.OAuthHandler(
        '', '')
    # access token, access token secret
    auth.set_access_token('',
                          '')

    api = tweepy.API(auth)
    return api


FIREBASE_API_KEY = '-'
FIREBASE_DOMAIN_LINKS_DOMAIN = ''
FIREBASE_DOMAIN_LINKS_TIMEOUT = 10

SPARKPOST_API_KEY = ''

AWS_ESCHERNODE_EMAIL_ACCESS_KEY = ''
AWS_ESCHERNODE_EMAIL_SECRET_KEY = ''

STRIPE_API_KEY_TEST = ""


# def create_api_from_creds(api_key, api_secret, access_token, access_token_secret):
#     auth = tweepy.OAuthHandler(api_key, api_secret)
#     auth.set_access_token(access_token, access_token_secret)
#     api = tweepy.API(auth)
#     return api
