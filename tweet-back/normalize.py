import re
import nltk
nltk.download('stopwords')
stop_words = nltk.corpus.stopwords.words('english')

def normalize(text: str, remove_stopwords=False, remove_tags=True):
    # lower case and remove special characters\whitespaces
    if(remove_tags):
        text = re.sub(r'[^a-zA-Z\s]', '', text, re.I|re.A)
    else:
        text = re.sub(r'[^a-zA-Z@#\s]', '', text, re.I|re.A)
    text = text.lower()
    text = text.strip()
    # tokenize document
    tokenizer = nltk.tokenize.TweetTokenizer()
    tokens = tokenizer.tokenize(text)
    if (remove_stopwords):
        tokens = [w for w in tokens if not w in stop_words]
    result = " ".join(tokens)
    return result

def normalize_(text: str):
    # lower case and remove special characters\whitespaces
    text = re.sub(r'[^a-zA-Z\s]', '', text, re.I|re.A)
    text = text.lower()
    text = text.strip()
    # tokenize document
    tokenizer = nltk.tokenize.TweetTokenizer()
    tokens = tokenizer.tokenize(text)
    tokens = [w for w in tokens if not w in stop_words]
    if (len(tokens) > 0 and tokens[0] == 'rt'):
        tokens.pop(0)
    result = " ".join(tokens)
    return result

def normalize_corpus(corpus):
    normalized_corpus = [normalize(text) for text in corpus]          
    return normalized_corpus

def tokenize(text: str):
    # lower case and remove special characters\whitespaces
    text = re.sub(r'[^a-zA-Z\s]', '', text, re.I|re.A)
    text = text.lower()
    text = text.strip()
    # tokenize document
    tokenizer = nltk.tokenize.TweetTokenizer()
    tokens = tokenizer.tokenize(text)
    remove_stopwords = [w for w in tokens if not w in stop_words]
    return remove_stopwords