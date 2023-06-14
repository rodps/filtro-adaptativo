import re
import trackwords

def remove_trackwords(text):
    text = re.sub(r'[^a-zA-Z\s]', '', text, re.I|re.A)
    text = [f for f in text.split() if not f in trackwords.base]
    return " ".join(text)

def get_keywords(norm_corpus):
    falses_norm = [remove_trackwords(f) for f in norm_corpus]
    f_keywords = dict()
    for f in falses_norm:
        words = f.split(" ")
        for w in words:
            if w in f_keywords:
                f_keywords[w] += 1
            else:
                f_keywords[w] = 1

    sorted_keywords = sorted(f_keywords.items(), key=lambda x: x[1], reverse=True)
    return sorted_keywords

def get_keywords_noremove(norm_corpus):
    f_keywords = dict()
    for f in norm_corpus:
        words = f.split(" ")
        for w in words:
            if w in f_keywords:
                f_keywords[w] += 1
            else:
                f_keywords[w] = 1

    sorted_keywords = sorted(f_keywords.items(), key=lambda x: x[1], reverse=True)
    return sorted_keywords

# def get_urls(urls):
#     urls_dict = dict()
#     for f in urls:
#         url_root = [x.group() for x in re.finditer(r"(https:\/\/)(?:www\.)*([.a-z0-9]+)+", f)]
#         for w in urls:
#             if w in urls_dict:
#                 urls_dict[w] += 1
#             else:
#                 urls_dict[w] = 1

#     sorted_keywords = sorted(urls_dict.items(), key=lambda x: x[1], reverse=True)
#     return sorted_keywords

def get_urls(urls):
    urls_dict = dict()
    for f in urls:
        x = re.search(r"(https:\/\/)(?:www\.)*([.a-z0-9]+)+", f)
        if (x):
            url_root = x.group()
            if url_root in urls_dict:
                urls_dict[url_root] += 1
            else:
                urls_dict[url_root] = 1

    sorted_keywords = sorted(urls_dict.items(), key=lambda x: x[1], reverse=True)
    return sorted_keywords