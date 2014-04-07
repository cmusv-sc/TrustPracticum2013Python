#!/usr/bin/env python

__version__='Sp2014'

import datetime
import math
import pymongo

import config

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
  coauthors = {}
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
  date = doc['mdate']
  doc_type = doc['type']
  return _time_factor(date)*config.type2weights[doc_type]
  
def _social_coauthorship_factor(doc):
  """
  Given a document, return the time factor. Passed into the map function and summed, the end goal becomes:
  Given an author, return SCF.
  SCF = \sum_{P_i} (#coauthorships in P_i) (scale factor for P_i)
  In this particlar implementation, we partition the space into recent, intermediate, and old.
  """
  date = doc['mdate']
  return _time_factor(date)

if __name__ == '__main__':
  db = pymongo.MongoClient()[config.DB_NAME]
  col = db[config.COLLECTION_NAME]
#  print _coauthorship_details(col, "Rajni Goel")
#  print _coauthorship_details(col, "Massimo Zancanaro")
  print _calculate_totals(_coauthorship_details_map(col, "Massimo Zancanaro", _social_coauthorship_factor))
  print math.ceil(_calculate_totals(_coauthorship_details_map(col, "Massimo Zancanaro", _publication_factor)))
