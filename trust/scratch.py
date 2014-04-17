#!/usr/bin/env python
"""
Various functions to calculate the trust model parameters.
"""

__version__='Sp2014'

import datetime
import math
import pymongo

import config
from db.scratch import *

def _calculate_totals(val_list):
  """
  Takes a list of tuples and returns the sum of the second element in each tuple.
  """
  return sum(map(lambda (x): x[1], val_list))

def _time_factor(date):
  """
  Takes a string date and returns the corresponding time factor defined in the config file.
  """
  date_object = datetime.datetime.strptime(date, '%Y-%m-%d')
  current_date_object = datetime.datetime.now()
  #Ignore leap years.
  time_diff = (current_date_object - date_object).days / 365.0
  if time_diff < config.recentYears:
    return config.tRecent
  elif time_diff < config.recentYears + config.intermediateYears:
    return config.tIntermediate
  else:
    return config.tOld

def _authorship_details_map(col, primary_author, fun_handle):
  """
  Map a function fun_handle over each document that primary_author authored. 
  """
  return_vals = []
  for doc in col.find({'author': {"$in": [primary_author]}}):
    return_vals.append(fun_handle(doc))
  return return_vals

def _coauthorship_details_map(col, primary_author, fun_handle):
  """
  Map a function fun_handle over each author in each document that primary_author authored. Returns a list of tuples (coauthor, return value of fun_handle(coauthor)).
  """
  return_vals = []
  for doc in col.find({'author': {"$in": [primary_author]}}):
    authors = doc['author']
    if isinstance(authors, list):
      for author in authors:
        if author != primary_author:
          return_vals.append((author, fun_handle(doc)))
  return return_vals

def _publication_factor(doc):
  """
  Given a document, return the time factor scaled by the publication type's alpha. The end goal is:

  Given an author, return the the publication factor for each of his/her publications, scale them by the appropriate alpha, and sum them up.
  """
  date = doc['mdate']
  doc_type = doc['type']
  return _time_factor(date)*config.type2weights[doc_type]

def _citation_factor(doc):
  """
  Given a document, return the number of citations scaled by the alpha of the publication type.
  """
  doc_type = doc['type']
  try:
    return len(doc['cite'])*config.type2weights[doc_type]
  except:
    return 0

def knowledge_factor(col, author, year=None):
  """
  Returns P_w K_{dblp, pub} + C_w K_{dblp, cite} + RT_w K_{TW, RT} as described in the technical document. For some reason, the Java code had a ceil throw in, so this has been ported as well.
  """
  if year is None:
    k_pub = math.ceil(sum(_authorship_details_map(col, author, _publication_factor)))
    k_cite = sum(_authorship_details_map(col, author, _citation_factor))
  else:
    k_pub = math.ceil(sum(authorship_details_map_before_year(col, author, _publication_factor, year)))
    k_cite = sum(authorship_details_map_before_year(col, author, _citation_factor, year))   
  return config.Pw * k_pub + config.Cw * k_cite

def _coauthorship_factor(doc):
  """
  Same thing as publication factor. Placeholder in case we want to make the methods different in the future.
  """
  return _publication_factor(doc)

def _combined_coauthorship_factor(col, primary_author, year=None):
  """
  For every coauthor the primary_author has, scales the coauthorship factor of each coauthor by the knowledge factor and sums up the results.
  """
  if year is None:
    lst = _coauthorship_details_map(col, primary_author, _coauthorship_factor)
  else:
    lst = coauthorship_details_map_before_year(col, primary_author, _coauthorship_factor, year)
  combined_coauthorship_val = 0
  for (coauthor, val) in lst:
    combined_coauthorship_val = combined_coauthorship_val + knowledge_factor(col, coauthor) * val
  return combined_coauthorship_val

if __name__ == '__main__':
  db = pymongo.MongoClient()[config.DB_NAME]
  col = db[config.COLLECTION_NAME]
#  print _coauthorship_details(col, "Rajni Goel")
#  print _coauthorship_details(col, "Massimo Zancanaro")
#  print _calculate_totals(_coauthorship_details_map(col, "Massimo Zancanaro", _coauthorship_factor))
#  print math.ceil(sum(_authorship_details_map(col, "Massimo Zancanaro", _publication_factor)))
#  print sum(_authorship_details_map(col, "Shahram Ghandeharizadeh", _citation_factor))
#  print knowledge_factor(col, "Shahram Ghandeharizadeh", 2014)
#  print knowledge_factor(col, "Luis Ramos", 2014)
#  print _combined_coauthorship_factor(col, "Shahram Ghandeharizadeh")
  print num_coauthors_in_range(col, "Shahram Ghandeharizadeh", 1800, 2014)
  
