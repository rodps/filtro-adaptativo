from normalize import normalize

def norm_text(status):
  return normalize(status['text'])

def map_norm(status):
  return status['norm']

def map_corpus(status):
  return status['extended_tweet']['full_text'] if status['truncated'] else status['text']

def map_user(status):
  return status['user']['screen_name']