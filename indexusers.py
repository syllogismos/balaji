from .config import create_api_from_creds
from tqdm import tqdm
from .utils import get_bulk_commands
import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
import tweepy
from backend.settings import es, rabbitmq_broker

# rabbitmq_broker = RabbitmqBroker()
dramatiq.set_broker(rabbitmq_broker)

index_name = "followers"


def get_limit_handled(cursor):
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            time.sleep(15 * 60)
        except StopIteration:
            return


@dramatiq.actor(max_retries=1, queue_name="index_followers", time_limit=7 * 24 * 60 * 60 * 1000)
def index_users(keys):
    # time limit for the worker process to run is 7 days for now
    # dramatiq balaji.indexusers --queues index_followers
    api = create_api_from_creds(
        keys['api_key'], keys['api_secret'], keys['access_token'], keys['access_token_secret'])
    me = api.me()
    i = me.followers_count
    followers = []
    try:
        for follower in tqdm(get_limit_handled(tweepy.Cursor(api.followers, count=200).items())):
            followers.append((follower, i))
            i -= 1
            if len(followers) > 20:
                bulk_commands = get_bulk_commands(
                    me, followers, index_name)
                es.bulk(body=bulk_commands)
                followers = []
        bulk_commands = get_bulk_commands(me, followers, index_name)
        es.bulk(body=bulk_commands)
    except:
        print("Exception while traversing the twitter api and indexing into es")
        pass
