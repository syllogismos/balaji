from collections import Counter
import re

regex = re.compile('[^a-z0-9\s]')

def flatten_string(string):
  return regex.sub('', string)

def get_tokens(f):
  """
  description
  status.text
  name
  """
  json_getter_1 = lambda f, c: f._json[c] if c in f._json else ''
  json_getter_2 = lambda follower, col, attr: f._json[col][attr] if col in f._json else ''
  col_getter = {
    'description': json_getter_1(f, 'description'),
    'status': json_getter_2(f, 'status', 'text'),
    'name': json_getter_1(f, 'name') 
  }
  text = flatten_string(' '.join(col_getter.values()).lower())
  
  return (f.id, text.split())

def get_counter(raw_followers):
  tokens = list(map(lambda x: get_tokens(x), raw_followers))
  l = list(map(lambda x: x[1], tokens))
  flat_list = [item for sublist in l for item in sublist]
  token_counter = Counter(flat_list)
  return token_counter

alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789'
most_common_words = ['as', 'I', 'his', 'that', 'he', 'was', 'for', 'on', 'are', 'with', 'they',
'be', 'at', 'one', 'have', 'this', 'from', 'by', 'hot', 'word', 'but', 'what', 'some', 'is', 'it',
'you', 'or', 'had', 'the', 'of', 'to', 'and', 'a', 'in', 'we', 'can', 'out', 'other', 'were', 'which',
'do', 'their', 'time', 'if', 'will', 'how', 'said', 'an', 'each', 'tell', 'does', 'set', 'three',
'want', 'air', 'well', 'also', 'play', 'small', 'end', 'put', 'home', 'read', 'hand', 'port',
'large', 'spell', 'add', 'even', 'land', 'here', 'must', 'big', 'high', 'such', 'follow', 'act',
'why', 'ask', 'men', 'change', 'went', 'light', 'kind', 'off', 'need', 'house', 'picture', 'try'
, 'us', 'again', 'animal', 'point', 'mother', 'world', 'near', 'build', 'self', 'earth', 'father'
, 'any', 'new', 'work', 'part', 'take', 'get', 'place', 'made', 'live', 'where', 'after', 'back',
'little', 'only', 'round', 'man', 'year', 'came', 'show', 'every', 'good', 'me', 'give', 'our',
'under', 'name', 'very', 'through', 'just', 'form', 'sentence', 'great', 'think', 'say', 'help',
'low', 'line', 'differ', 'turn', 'cause', 'much', 'mean', 'before', 'move', 'right', 'boy', 'old',
'too', 'same', 'she', 'all', 'there', 'when', 'up', 'use', 'your', 'way', 'about', 'many', 'then',
'them','write','would','like','so','these','her','long','make','thing','see','him','two','has','look','more','day','could','go','come','did','number','sound','no','most','people','my','over','know','water','than','call','first','who','may','down','side','been','now','find','head','stand','own','page','should','country','found','answer','school','grow','study','still','learn','plant','cover','food','sun','four','between','state','keep','eye','never','last','let','thought','city','tree','cross','farm','hard','start','might','story','saw','far','sea','draw','left','late','run','don’t','while','press','close','night','real','life','few','north','book','carry','took','science','eat','room','friend','began','idea','fish','mountain','stop','once','base','hear','horse','cut','sure','watch','color','face','wood','main','open','seem','together','next','white','children','begin','got','walk','example','ease','paper','group','always','music','those','both','mark','often','letter','until','mile','river','car','feet','care','second','enough','plain','girl','usual','young','ready','above','ever','red','list','though','feel','talk','bird','soon','body','dog','family','direct','pose','leave','song','measure','door','product','black','short','numeral','class','wind','question','happen','complete','ship','area','half','rock','order','fire','south','problem','piece','told','knew','pass','since','top','whole','king','street','inch','multiply','nothing','course','stay','wheel','full','force','blue','object','decide','surface','deep','moon','island','foot','system','busy','test','record','boat','common','gold','possible','plane','stead','dry','wonder','laugh','thousand','ago','ran','check','game','shape','equate','hot','miss','brought','heat','snow','tire','bring','yes','distant','fill','east','paint','language','among','unit','power','town','fine','certain','fly','fall','lead','cry','dark','machine','note','wait','plan','figure','star','box','noun','field','rest','correct','able','pound','done','beauty','drive','stood','contain','front','teach','week','final','gave','green','oh','quick','develop','ocean','warm','free','minute','strong','special','mind','behind','clear','tail','produce','fact','space','heard','best','hour','better','true','during','hundred','five','remember','step','early','hold','west','ground','interest','reach','fast','verb','sing','listen','six','table','travel','less','morning','ten','simple','several','vowel','toward','war','lay','against','pattern','slow','center','love','person','money','serve','appear','road','map','rain','rule','govern','pull','cold','notice','voice']

most_common_words.extend(alphabet)
most_common_words.extend(['rt', 'twitter'])

most_common_words = list(map(lambda x: x.lower(), most_common_words))
raw_followers = []
tc = get_counter(raw_followers)
v = list(filter(lambda x: x[0] not in most_common_words and x[1] > 5, tc.items()))
sorted(v, key=lambda x: x[1], reverse=True)[:100]