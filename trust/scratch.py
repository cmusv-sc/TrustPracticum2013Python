#!/usr/bin/env python

__version__='Sp2014'

import datetime
import pymongo

import config

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

def _coauthorship_details(col, primary_author):
  """
  Given an author, returns a mapping from coauthors to coauthorship date.
  """
  coauthors = {}
  for doc in col.find({'author': {"$in": [primary_author]}}):
    authors = doc['author']
    if isinstance(authors, list):
      for author in authors:
        if author != primary_author:
          if author not in coauthors:
            coauthors[author] = []
          temp = coauthors[author]
          temp.append(doc['mdate'])
          coauthors[author] = temp
  return coauthors

def _coauthorship_details_map(col, primary_author, fun_handle):
  """
  Map a function fun_handle over each document that primary_author authored.
  """
  coauthors = {}
  return_vals = []
  for doc in col.find({'author': {"$in": [primary_author]}}):
    return_vals.append(fun_handle(doc))
  return return_vals

def _social_coauthorship_factor(col, primary_author):
  """
  Given an author, returns mapping from coauthors to social coauthorship factor (SCF). Given a partion of the time space P = {P_i}:
  SCF = \sum_{P_i} (#coauthorships in P_i) (scale factor for P_i)
  In this particlar implementation, we partition the space into recent, intermediate, and old.
  """
  coauthor2scf = {}
  coauthor_details = _coauthorship_details(col, primary_author)
  for coauthor in coauthor_details:
    scf = 0
    for date in coauthor_details[coauthor]:
      scf = scf + _time_factor(date)
    coauthor2scf[coauthor] = scf
  return coauthor2scf

def _publication_factor(col, primary_author):
  pass

def _social_coauthorship_factor_mapper(doc):
  date = doc['mdate']
  return _time_factor(date)

if __name__ == '__main__':
  db = pymongo.MongoClient()[config.DB_NAME]
  col = db[config.COLLECTION_NAME]
#  print _coauthorship_details(col, "Rajni Goel")
#  print _coauthorship_details(col, "Massimo Zancanaro")
  print sum(_social_coauthorship_factor(col, "Massimo Zancanaro").values())
  print sum(_coauthorship_details_map(col, "Massimo Zancanaro", _social_coauthorship_factor_mapper))
