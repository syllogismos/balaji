from .utils import create_api_user_access_tokens

from balaji.filters import getESQueryFromFilters
import datetime

import dramatiq
import tweepy
from backend.settings import db, get_user, es, rabbitmq_broker

dramatiq.set_broker(rabbitmq_broker)

db_index = 'dms'


def get_limit_handled(cursor):
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            time.sleep(15 * 60)
        except StopIteration:
            return


@dramatiq.actor(max_retries=0, queue_name="start_campaign", time_limit=1 * 60 * 60 * 100)
def run_campaign(campaign_id):
    campaign = db.collection('campaigns').document(campaign_id).get().to_dict()
    uid = campaign["uid"]
    user_details = db.collection('userdetails').document(uid).get().to_dict()
    api = create_api_user_access_tokens(user_details)
    escher_user = api.me()
    filters = campaign['data']['filters']['filters']
    es_query = getESQueryFromFilters(
        filters, escher_user.id_str, 1000, source_fields=["id_str"])
    es_response = es.search(index="fol*", body=es_query)
    es_ids = set(map(lambda x: x['_source']
                     ['id_str'], es_response['hits']['hits']))
    dm = campaign['data']['dm']
    print(es_ids)
    for id_str in es_ids:
        try:
            api.send_direct_message(id_str, dm)
            es.index('dms', body={'dm': dm, 'escher_account': escher_user.id_str,
                                  'id_str': id_str, 'campaign': campaign_id, 't': datetime.datetime.now()})
        except Exception as e:
            print(e)
            print(campaign_id, 'sending dm to', id_str, 'failed')
