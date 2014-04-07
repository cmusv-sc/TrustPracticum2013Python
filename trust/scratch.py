#!/usr/bin/env python

__version__='Sp2014'

import pymongo

import config

def _time_factor(doc):
  return doc['mdate']

def _coauthorship_details(col, primary_author):
  """
  Given an author, returns a mapping from coauthors to a list of dates when they collaborated.
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

def _social_coauthorship_factor(col, author):
  """
  Given an author, returns mapping from coauthors to social coauthorship factor (SCF). Given a partion of the time space P = {P_i}:
  SCF = \sum_{P_i} (#coauthorships in P_i) (scale factor for P_i)
  In this particlar implementation, we partition the space into recent, intermediate, and old.
  """
  pass

if __name__ == '__main__':
  db = pymongo.MongoClient()[config.DB_NAME]
  col = db[config.COLLECTION_NAME]
  print _coauthorship_details(col, "Rajni Goel")

