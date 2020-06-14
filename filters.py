from config import BASE_JSON



def get_followers_from_json():
  followers = json.load(open(BASE_JSON, 'rb'))
  return followers

def country_code_filter(followers, code):
  return list(filter(lambda x: x['country_code']==code, followers))

