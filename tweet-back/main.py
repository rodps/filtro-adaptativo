from fastapi import FastAPI
from pymongo import MongoClient
import pandas as pd
from map_corpus import map_norm, map_corpus, map_user
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from bson import json_util
import json
import uuid
from normalize import normalize, normalize_corpus, normalize_
from urllib.parse import urlparse
from jaccard import jaccard
import re
from get_keywords import get_keywords, get_keywords_noremove, get_urls
import urlexpander

client = MongoClient("")
db = client['cybersecurity']
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/clusters")
async def clusters(page: int = 1):
  page = page if page > 0 else 1
  page_size = 100
  skip = (page - 1) * page_size
  result = db.tweets.find({'retweeted_status': {'$exists': 0}, 'quoted_status': {'$exists': 0}}, {'_id': 0}).skip(skip).limit(page_size)
  list_cur = list(result)

  for status in list_cur:
    text = status['extended_tweet']['full_text'] if status['truncated'] else status['text']
    status['full_text'] = text 
    status['norm'] = normalize(text)

    urls = status['extended_tweet']['entities']['urls'] if status['truncated'] else status['entities']['urls']
    extended_urls = []
    for u in urls:
      extended_urls.append(urlexpander.expand(u['expanded_url']))
    status['urls'] = extended_urls

  blocked_keywords = list(db.filters.find({'type': 'keyword' }, {'_id': 0}))
  blocked_urls = list(db.filters.find({'type': 'url' }, {'_id': 0}))
  blocked_users = list(db.filters.find({'type': 'user' }, {'_id': 0}))
  falses = list(db.processados.find({'label': 'F' }, {'_id': 0}))
  falses_corpus = [tweet['tweets'][0]['tweet'] for tweet in falses]

  falses_norm = [normalize(f, True) for f in falses_corpus]
  sorted_keywords = get_keywords(falses_norm)

  #filters
  def filter_len(status):
    words = normalize(status['full_text'], remove_tags=False)
    words = words.split()
    words_remove_tags = [w for w in words if (w[0] != '@' and w[0] != '#')]
    word_count = len(words_remove_tags)
    if (word_count > 3):
      return True
    else:
      db.descartados.insert_one({'tweet': status, 'motivo': 'tamanho', 'valor': word_count})
      return False
  
  def filter_keywords(status):
    text = status["full_text"].lower()
    for k in blocked_keywords:
      keyword = k["text"].lower()
      if (text.find(keyword) != -1):
        db.descartados.insert_one({'tweet': status, 'motivo': 'keyword', 'valor': keyword})
        return False
    return True

  def filter_urls(status):
    status_urls = status['urls']
    for k in blocked_urls:
      for url in status_urls:
        if (url.find(k["text"]) != -1):
          db.descartados.insert_one({'tweet': status, 'motivo': 'url', 'valor': k["text"]})
          return False
    return True

  def filter_users(status):
    user = status["user"]["id_str"]
    for k in blocked_users:
      if (k["text"] == user):
        db.descartados.insert_one({'tweet': status, 'motivo': 'user', 'valor': k["text"]})
        return False
    return True

  def filter_similars(status):
    top_keywords = sorted_keywords[:10]
    top_keywords_number = 0
    for v in top_keywords:
      top_keywords_number += v[1]

    keyword_score = 0
    for v in top_keywords:
      word = v[0].lower()
      tweet = status['full_text'].lower()
      if (tweet.find(word) != -1):
        keyword_score += v[1]/top_keywords_number

    falses_f = [tweet['tweets'][0] for tweet in falses]
    tweet = status['norm']
    for false in falses_f:
      jaccard_score = jaccard(false['full']['norm'], tweet)
      score = jaccard_score + keyword_score
      if (score >= 0.5):
        db.descartados.insert_one({'tweet': status, 'motivo': 'similar', 'valor': {
          'false': {
            'full': false['tweet'],
            'norm': false['full']['norm']
          },
          'tweet': {
            'full': status['full_text'],
            'norm': status['norm']
          },
          'jaccard_score': jaccard_score,
          'keyword_score': keyword_score,
          'total_score': score
        }})
        return False
    return True

  filtered = list(filter(filter_len, list_cur))
  filtered = list(filter(filter_keywords, filtered))
  filtered = list(filter(filter_urls, filtered))
  filtered = list(filter(filter_users, filtered))
  if len(falses_corpus) > 0:
    filtered = list(filter(filter_similars, filtered))

  from clustering import jaccard_cluster
  norm_corpus = list(map(map_norm, filtered))
  cluster_labels = jaccard_cluster(norm_corpus)

  tweets = {'tweet': map(map_corpus, filtered), 'user': map(map_user, filtered), 'cluster': cluster_labels, 'full': filtered}
  df = pd.DataFrame(data=tweets)
  df_list = df.to_dict(orient='records')
  arrange = dict()
  for x in cluster_labels:
    arrange[str(x)] = list()
  for item in df_list:
    arrange[str(item['cluster'])].append(item)
  for key, value in arrange.items():
    if (key == '-1'):
      for x in value:
        db.processados.insert_one({'cluster_id': str(uuid.uuid4()), 'label': 'N', 'page': page, 'tweets': [x]})
    else:
      db.processados.insert_one({'cluster_id': str(uuid.uuid4()), 'label': 'N', 'page': page, 'tweets': value})

@app.get("/tweets")
async def tweets():
  result = db.processados.find({ 'label': 'N' }, {'_id': 0})
  response = json.loads(json_util.dumps(result))
  return response

@app.post("/filters")
async def filters(request: Request):
  filter = await request.json()
  db.filters.insert_one(filter)

@app.get("/filters")
async def filters(type: str):
  filters = db.filters.find({'type': type})
  response = json.loads(json_util.dumps(filters))
  return response


@app.post("/down/cluster/{id}")
async def down(id: str):
  cluster = db.processados.find_one({ 'cluster_id': id })
  db.processados.update_one({ 'cluster_id': id }, { '$set': { 'label': 'F' } })

@app.post("/up/cluster/{id}")
async def up(id: str):
  db.processados.update_one({ 'cluster_id': id }, { '$set': { 'label': 'V' } })


@app.get("/restart")
async def restart():
  db.filters.delete_many({})
  db.processados.delete_many({})
  db.descartados.delete_many({})

@app.get("/keywords")
async def keywords():
  falses = list(db.processados.find({'label': 'F' }, {'_id': 0}))
  falses_corpus = [tweet['tweets'][0]['tweet'] for tweet in falses]
  falses_norm = [normalize(f, True) for f in falses_corpus]
  sorted_keywords = get_keywords(falses_norm)
  response = json.loads(json_util.dumps(sorted_keywords))
  return response

@app.get("/topkeywords")
async def topkeywords():
  tweets = list(db.tweets.find({}, {'_id': 0}))
  corpus = [t['extended_tweet']['full_text'] if t['truncated'] else t['text'] for t in tweets]
  corpus_norm = [normalize_(c) for c in corpus]
  sorted_keywords = get_keywords_noremove(corpus_norm)
  response = json.loads(json_util.dumps(sorted_keywords))
  return response

# @app.get("/topurls")
# async def topurls():
#   print('getting tweets...')
#   tweets = list(db.tweets.find({'retweeted_status': {'$exists': 0}, 'quoted_status': {'$exists': 0}}, {'_id': 0}))
#   print('get tweets ok')
#   print(f'{len(tweets)} tweets encontrados')
#   urls = [t['extended_tweet']['entities']['urls'] if t['truncated'] else t['entities']['urls'] for t in tweets]
#   expanded_urls = []
#   for u in urls:
#     expanded_urls = expanded_urls + [t['expanded_url'] for t in u]
#   # for t in corpus:
#   #   urls = urls + []
#     # urls = urls + [x.group() for x in re.finditer(r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)", t)]
#   print('ulrs ok')
#   print(f'{len(expanded_urls)} urls encontradas')
#   for u in expanded_urls:
#     try:
#       expanded = urlexpander.expand(u)
#       db.urls_tweets.insert_one({ 'url': expanded })        
#     except:
#       print("An exception occurred")
#   print('expanded urls ok')

@app.get("/geturls")
async def geturls():
  print('getting urls')
  result = list(db.urls_tweets.find({}, {'_id': 0}))
  print('get urls ok')
  print(f'{len(result)} urls encontradas')
  urls = [u['url'] for u in result]
  print('sorting urls')
  sorted_urls = get_urls(urls)
  response = json.loads(json_util.dumps(sorted_urls))
  return response

@app.get("/getfalseurls")
async def getfalseurls():
  print('getting urls')
  falses = list(db.processados.find({'label': 'F' }, {'_id': 0}))
  falses_urls = []
  for tweet in falses:
    falses_urls = falses_urls + tweet['tweets'][0]['full']['urls']
  print(f'{len(falses_urls)} urls encontradas')
  print("sorting urls")
  sorted_urls = get_urls(falses_urls)
  response = json.loads(json_util.dumps(sorted_urls))
  return response