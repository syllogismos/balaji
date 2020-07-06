from .utils import create_api_user_access_tokens
from tqdm import tqdm
from .utils import get_bulk_commands, get_bulk_commands_follower_ids, get_bulk_commands_user_deets
import dramatiq
from dramatiq.brokers.rabbitmq import RabbitmqBroker
import tweepy
import traceback
import time
from backend.settings import es, rabbitmq_broker, db
from elasticsearch.helpers import scan

# rabbitmq_broker = RabbitmqBroker()
dramatiq.set_broker(rabbitmq_broker)

index_name = "followers"
fast_index_name = "followers_fast"

TWEEPY_ID_LIMIT = 50
TWEEPY_USER_DEETS_LIMIT = 3


def get_limit_handled(cursor):
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            time.sleep(15 * 60)
        except StopIteration:
            return


@dramatiq.actor(max_retries=0, queue_name="index_followers", time_limit=7 * 24 * 60 * 60 * 1000)
def index_users(uid):
    # time limit for the worker process to run is 7 days for now
    # dramatiq balaji.indexusers --queues index_followers
    user_details = db.collection(u'userdetails').document(uid).get().to_dict()
    if 'index_status' in user_details and user_details['index_status'] == 'indexing':
        return
    try:
        api = create_api_user_access_tokens(user_details)
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


@dramatiq.actor(max_retries=0, queue_name="index_followers_fast", time_limit=24*60*60*100)
def index_users_fast(uid):
    # time limit for the worker process to run is 1 day
    # dramatiq balaji.indexusers --queues index_followers_fast
    user_details = db.collection('userdetails').document(uid).get().to_dict()
    if 'index_status' in user_details and user_details['index_status'] == 'indexing':
        return
    try:
        api = create_api_user_access_tokens(user_details)
        me = api.me()
        db.collection('userdetails').document(uid).set(
            {'index_status': 'indexing'}, merge=True
        )

        # INDEX FOLLOWER IDS
        i = me.followers_count
        follower_ids = []
        for follower_id in tqdm(get_limit_handled(tweepy.Cursor(api.followers_ids, count=TWEEPY_ID_LIMIT).items())):
            follower_ids.append((follower_id, i))
            i -= 1
            if len(follower_ids) > TWEEPY_ID_LIMIT:
                bulk_commands = get_bulk_commands_follower_ids(
                    me, follower_ids, fast_index_name)
                es.bulk(body=bulk_commands)
                follower_ids = []
        bulk_commands = get_bulk_commands_follower_ids(
            me, follower_ids, fast_index_name)
        es.bulk(body=bulk_commands)
        db.collection('userdetails').document(uid).set(
            {'index_status': 'ids_finished'}, merge=True)

        # QUERY FOR FOLLOWER IDS FROM ES AND GET FOLLOWER DEETS FROM TWITTER
        scan_query = {'_source': ['escher_account', 'id_str'],
                      'query': {'term': {'escher_account': me.id_str}}}
        es_scan_gen = scan(es, query=scan_query, scroll="20m",
                           index=fast_index_name)
        follower_ids_from_es = []
        followers = []
        for scan_obj in es_scan_gen:
            if len(follower_ids_from_es) == TWEEPY_USER_DEETS_LIMIT:
                while True:
                    try:
                        followers.append(
                            api.lookup_users(follower_ids_from_es))
                        follower_ids_from_es = []
                        break
                    except tweepy.RateLimitError:
                        print("Tweepy lookup users ratelimit")
                        time.sleep(15 * 60)
            if len(followers) > TWEEPY_USER_DEETS_LIMIT:
                bulk_commands = get_bulk_commands_user_deets(
                    me, followers, fast_index_name)
                es.bulk(body=bulk_commands)
                followers = []

            follower_ids_from_es.append(scan_obj['_source']['id_str'])

        if len(follower_ids_from_es) > 0:
            while True:
                try:
                    followers.append(api.lookup_users(follower_ids_from_es))
                    break
                except tweepy.RateLimitError:
                    print("Tweepy lookup users ratelimit")
                    time.sleep(15 * 60)
        if len(followers) > 0:
            bulk_commands = get_bulk_commands_user_deets(
                me, followers, fast_index_name)
            es.bulk(body=bulk_commands)
        db.collection(u'userdetails').document(uid).set(
            {'index_status': 'finished'}, merge=True)
    except Exception as e:
        print("Exception while fast indexing from twitter api")
        traceback.print_exception(e)
        db.collection(u'userdetails').document(uid).set(
            {'index_status': 'failed'}, merge=True)
