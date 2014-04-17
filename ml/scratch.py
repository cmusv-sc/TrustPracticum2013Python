#!/usr/bin/env python
"""
Naive Bayes implementation
"""

__version__='Sp2014'

import config
from db.scratch import *

import math
import pymongo

def _get_jaccard_info(doc):
  """
  Returns a list containing [author_1,.., author_n, journal]. If journal doesn't exist, returns [author_1, ..., author_n]
  """
  return_val = []
  authors = doc['author']
  if isinstance(authors, list):
    for author in doc['author']:
      return_val.append(author)
  else:
    return_val.append(authors)
  if 'journal' in doc:
    return_val.append(doc['journal'])
  return return_val

def _flatten_list(lst):
  return [item for sublist in lst for item in sublist]

def jaccard_similarity(col, author1, author2):
  """
  Returns the jaccard similarity = |s1 \cap s2| / |s1 \cup s2|. Where s1 and s2 are the sets containing the titles and journals of each publication of author1 and author 2 respectively.
  """
  s1 = set(_flatten_list(authorship_details_map(col, author1, _get_jaccard_info)))
  s2 = set(_flatten_list(authorship_details_map(col, author2, _get_jaccard_info)))
  return float(len(s1.intersection(s2)))/len(s1.union(s2))

def get_coauthor_distance_before_year(col, primary_author, coauthor, year):
  for doc in col.find({'author': {"$in": [primary_author]}, 'year' : {"$lt": str(year)}}):
    if coauthor in doc['author']:
      return 1
  for doc in col.find({'author': {"$in": [primary_author]}, 'year' : {"$lt": str(year)}}):
    author_list = doc['author']
    if not isinstance(author_list, list):
      author_list = [author_list]
    for author in author_list:
      for doc2 in col.find({'author': {"$in": [author]}, 'year' : {"$lt": str(year)}}):
        if coauthor in doc2['author']:
          return 2
  return 999
    
if __name__ == '__main__':
  db = pymongo.MongoClient()[config.DB_NAME]
  col = db[config.COLLECTION_NAME]
#  s1 = set(_flatten_list(authorship_details_map(col, 'Luis Ramos', _get_jaccard_info)))
#  s2 = set(_flatten_list(authorship_details_map(col, 'Shahram Ghandeharizadeh', _get_jaccard_info)))
#  print s1.union(s2)
#  print s1.intersection(s2)
#  print jaccard_similarity(col, 'Luis Ramos', 'Shahram Ghandeharizadeh')
#  print authorship_details_map_before_year(col, 'Luis Ramos', lambda(x): x, 2000)
  #db.documents.find('this.year < 1999 && this.author.indexOf("Luis Ramos") > -1')
# Should return 1
#  print get_coauthor_distance_before_year(col, 'Luis Ramos', 'Shahram Ghandeharizadeh', 2013)
# Should return 2
#  print get_coauthor_distance_before_year(col, 'Luis Ramos', 'David J. DeWitt', 2013)
# Should return 999
#  print get_coauthor_distance_before_year(col, 'Luis Ramos', 'qqqqqqqqqqq', 2013)

  

