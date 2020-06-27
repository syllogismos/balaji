from .config import create_api_from_creds
from tqdm import tqdm
from .utils import get_bulk_commands
import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
import tweepy
from backend.settings import es, rabbitmq_broker, db

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
def index_users(uid):
    # time limit for the worker process to run is 7 days for now
    # dramatiq balaji.indexusers --queues index_followers
    user_details = db.collection(u'userdetails').document(uid).get().to_dict()
    if 'index_status' in user_details and user_details['index_status'] == 'indexing':
        return
    try:
        api = create_api_from_creds(
            user_details['api_key'],
            user_details['api_secret'],
            user_details['access_token'],
            user_details['access_token_secret'])
        me = api.me()
        db.collection(u'userdetails').document(uid).set(
            {'index_status': 'indexing'}, merge=True)
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
            db.collection(u'userdetails').document(uid).set(
                {'index_status': 'finished'}, merge=True)
        except Exception as e:
            print("Exception while traversing the twitter api and indexing into es", e)
            pass
    except Exception as e:
        print("Exception while querying the twitter api", e)
        db.collection(u'userdetails').document(uid).set(
            {'index_status': 'failed'}, merge=True)
