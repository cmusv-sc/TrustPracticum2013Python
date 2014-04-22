#! /usr/bin/env python
import pymongo
import re
import sys

import config
if __name__ == '__main__':
  db = pymongo.MongoClient()[config.DB_NAME]
  col = db[config.COLLECTION_NAME]
  author_list = []
  for doc in col.find():
    if 'author' in doc:
      authors = doc['author']
      if isinstance(authors, list):
        author_list.extend(authors)
      else:
        author_list.append(authors)
  author_list = set(author_list)
  for author in author_list:
    print author
