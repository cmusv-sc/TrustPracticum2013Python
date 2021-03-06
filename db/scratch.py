#! /usr/bin/env python
"""
Takes dblp xml from stdin and pushes it to a mongodb
Usage:
cat dblp.xml | python -m db.scratch
"""
__version__='Sp2014'

import pymongo
import re
import sys

import config

def authorship_details_map(col, primary_author, fun_handle):
  """
  Map a function fun_handle over each document that primary_author authored. 
  """
  return_vals = []
  for doc in col.find({'author': {"$in": [primary_author]}}):
    return_vals.append(fun_handle(doc))
  return return_vals

def authorship_details_map_before_year(col, primary_author, fun_handle, year):
  """
  Map a function fun_handle over each document that primary_author authored before year.
  """
  return_vals = []
  for doc in col.find({'author': {"$in": [primary_author]}, 'year' : {"$lt": year}}):
    return_vals.append(fun_handle(doc))
  return return_vals

def coauthorship_details_map_before_year(col, primary_author, fun_handle, year):
  """
  Map a function fun_handle over each author in each document that primary_author authored before year. Returns a list of tuples (coauthor, return value of fun_handle(coauthor)).
  """
  return_vals = []
  for doc in col.find({'author': {"$in": [primary_author]}, 'year' : {"$lt": year}}):
    authors = doc['author']
    if isinstance(authors, list):
      for author in authors:
        if author != primary_author:
          return_vals.append((author, fun_handle(doc)))
  return return_vals

def num_coauthors_in_range(col, primary_author, start=1800, end=2014):
  author_list = []
  for doc in col.find({'author': {"$in": [primary_author]}, 'year' : {"$lt": end, "$gt": start}}):
    authors = doc['author']
    if isinstance(authors, list):
      author_list.extend(authors)
    else:
      author_list.append(authors)
  author_list = set(author_list)
  return len(author_list) - 1

#Just so code is a bit more readable
def strip_quotes(s):
  return re.sub('"','',s)

if __name__ == '__main__':
  db = pymongo.MongoClient()[config.DB_NAME]
  print config.DB_NAME
  doc = {}
  for line in sys.stdin:
    start = re.search('<((article)|(inproceedings)|(proceedings)|(book)|(incollection)|(phdthesis)|(mastersthesis)|(www))',line)
    end = re.search('</((article)|(inproceedings)|(proceedings)|(book)|(incollection)|(phdthesis)|(mastersthesis)|(www))',line)
    if start:
      doc['type'] =  strip_quotes(start.groups()[0])
      tag_attributes = re.findall(' (.+?)=(.+?)(?=[ >])',line)
      for attr in tag_attributes:
        doc[attr[0]] = strip_quotes(attr[1])
      #Sometimes, there's an extra tag on the same line.
      extra_tag = re.search('.+?> <(.+?)>(.+?)</(.+?)>', line)
      if extra_tag:
        groups = extra_tag.groups()
        doc[groups[0]] = strip_quotes(groups[1])
    elif end:
      db['documents'].insert(doc)
      doc = {}
    else:
      element = re.search('<(.+?)>(.+?)</',line)
      if element:
        tag_attributes = re.findall(' (.+?)=(.+?)(?=[ >])',line)
        groups = element.groups()
        #Nested attributes. Need to clean out tag name
        if tag_attributes != [] and len(groups) == 2:
          tag_name = re.search('<(.+?) ',line).groups()[0]
          sub_doc = {tag_name: strip_quotes(groups[1])}
          for attr in tag_attributes:
            sub_doc[attr[0]] = strip_quotes(attr[1])
        elif len(groups) == 2:
          tag_name = groups[0]
          tag_info = groups[1]
          if tag_name in doc:
            prev_info = doc[tag_name]
            if isinstance(prev_info, list):
              prev_info.append(tag_info)
              doc[tag_name] = prev_info
            else:
              doc[tag_name] = [prev_info, tag_info]
          elif tag_name == 'year':
            tag_info = int(tag_info)
            doc[tag_name] = tag_info
          else:
            doc[tag_name] = strip_quotes(tag_info)
        else:
          print 'This should not happen'
