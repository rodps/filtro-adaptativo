from jaccard import jaccard

def jaccard_cluster(corpus):
  labels = [None] * len(corpus)
  l = 0
  for k1, v1 in enumerate(corpus):
      for k2, v2 in enumerate(corpus):
        if jaccard(v1, v2) >= 0.5:
          label = labels[k1] if labels[k1] else labels[k2]
          if not label:
            l += 1
            label = l
          labels[k1] = label
          labels[k2] = label
  return labels