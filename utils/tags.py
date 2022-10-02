import os
# import nltk
# assert(nltk.download('wordnet'))  # Make sure we have the wordnet data.
# from nltk.corpus import wordnet as wn
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import os

module_url = "https://tfhub.dev/google/universal-sentence-encoder/4" 
model = hub.load(module_url)
print ("module %s loaded" % module_url)

def get_tags(caption, tags):
    tags_found = []
    caption_embedding = model(caption)[0]
    tag_embedings = model(tags)
    for embedding in tag_embeddings:
        similarity = np.linalg.norm(np.array(embedding) - np.array(caption_embedding))
        if similarity > 0.7:
            tags_found.append(tag)
    # todo: implement length counterbalance
        
    return tags_found

def get_timeline(caption_timeline, tags_timeline, tags):
    for i in tags_timeline.keys():
        tags = get_tags(caption_timeline[i], tags)
        tag_timeline[i] = tags
    return tag_timeline