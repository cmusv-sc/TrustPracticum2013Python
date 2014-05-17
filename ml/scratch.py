#!/usr/bin/env python
"""
Naive Bayes implementation
"""

__version__='Sp2014'

import config
from db.scratch import *
import trust.scratch as trust

import math
import pymongo

def _get_jaccard_info(doc):
  """
  Returns a list containing [author_1,.., author_n, journal]. If journal doesn't exist, returns [author_1, ..., author_n]
  """
  return_val = []
  authors = doc['author']
  if isinstance(authors, list):
    return_val.extend(authors)
  else:
    return_val.append(authors)
  if 'journal' in doc:
    journals = doc['journal']
    if isinstance(journals, list):
      return_val.extend(journals)
    else:
      return_val.append(journals)
  return return_val

def _flatten_list(lst):
  return [item for sublist in lst for item in sublist]

def jaccard_similarity(col, author1, author2):
  """
  Returns the jaccard similarity = |s1 \cap s2| / |s1 \cup s2|. Where s1 and s2 are the sets containing the titles and journals of each publication of author1 and author 2 respectively.
  """
  s1 = set(_flatten_list(authorship_details_map(col, author1, _get_jaccard_info)))
  s2 = set(_flatten_list(authorship_details_map(col, author2, _get_jaccard_info)))
  try:
    return float(len(s1.intersection(s2)))/len(s1.union(s2))
  except:
    return 0
  
def get_coauthor_distance_before_year(col, primary_author, coauthor, year):
  for doc in col.find({'author': {'$in': [primary_author]}, 'year' : {'$lt': 2014}}):
    if coauthor in doc['author']:
      return 1
  for doc in col.find({'author': {"$in": [primary_author]}, 'year' : {"$lt": year}}):
    author_list = doc['author']
    if not isinstance(author_list, list):
      author_list = [author_list]
    for author in author_list:
      for doc2 in col.find({'author': {"$in": [author]}, 'year' : {"$lt": year}}):
        if coauthor in doc2['author']:
          return 2
  return 999

def write_line_for_authors(col, author1, author2, year):
  """
  Decides whether each feature falls into H, M, or L regions for given authors. Returns results separated by commas.
  """
  year = int(year)
  author1 = author1.strip()
  author2 = author2.strip()
  coauthor_distance = get_coauthor_distance_before_year(col, author1, author2, year)
  trust_value_difference = trust.trust_value(col, author1, year) - trust.trust_value(col, author1, year)
  jaccard_val = jaccard_similarity(col, author1, author2)
  coauthorship_history1 = num_coauthors_in_range(col, author1, end=year)
  coauthorship_history2 = num_coauthors_in_range(col, author2, end=year)
  effective_coauthorship = min(coauthorship_history1, coauthorship_history2)
  line = ""
  if coauthor_distance == 1:
    cd_line = "Y"
  else:
    cd_line = "N"
  #Needs to be tuned  
  if jaccard_val >= 0.5:
    j_line = "H"
  elif jaccard_val < 0.5 and jaccard_val >= 0.25:
    j_line = "M"
  else:
    j_line = "L"

  if coauthor_distance <= 1:
    cd_line2 = "H"
  elif coauthor_distance <=2 and coauthor_distance > 1:
    cd_line2 = "M"
  else:
    cd_line2 = "L"

  if trust_value_difference < 0:
    tv_line = "H"
  elif trust_value_difference >=0 and trust_value_difference <= 1:
    tv_line = "M"
  else:
    tv_line = "L"

  if effective_coauthorship > 5:
    ec_line = "H"
  elif effective_coauthorship <= 5 and effective_coauthorship > 1:
    ec_line = "M"
  else:
    ec_line = "L"
  return "{0},{1},{2},{3},{4}".format(cd_line, j_line, cd_line2, tv_line, ec_line)
    
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
  #print write_line_for_authors(col, 'Luis Ramos', 'Shahram Ghandeharizadeh', 2000)
  print write_line_for_authors(col, 'Luis Ramos', 'Luis Ramos', 2000)

  

