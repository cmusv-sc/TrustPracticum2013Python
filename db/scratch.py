#! /usr/bin/env python
import pymongo
import re
import sys

import config

if __name__ == '__main__':
  db = pymongo.MongoClient()[config.DB_NAME]
  print config.DB_NAME
  doc = {}
  for line in sys.stdin:
    start = re.match('<((article)|(inproceedings)|(proceedings)|(book)|(incollection)|(phdthesis)|(mastersthesis)|(www))',line)
    end = re.match('</((article)|(inproceedings)|(proceedings)|(book)|(incollection)|(phdthesis)|(mastersthesis)|(www))',line)
    if start:
      doc['type'] =  start.groups()[0]
      tag_attributes = re.findall(' (.+?)=(.+?)(?=[ >])',line)
      for attr in tag_attributes:
        doc[attr[0]] = attr[1]
    elif end:
      db['documents'].insert(doc)
      doc = {}
    else:
      element = re.match('<(.+?)>(.+?)</',line)
      if element:
        tag_attributes = re.findall(' (.+?)=(.+?)(?=[ >])',line)
        groups = element.groups()
        #Nested attributes. Need to clean out tag name
        if tag_attributes != [] and len(groups) == 2:
          tag_name = re.search('<(.+?) ',line).groups()[0]
          sub_doc = {tag_name: groups[1]}
          for attr in tag_attributes:
            sub_doc[attr[0]] = attr[1]
        elif len(groups) == 2:
          doc[groups[0]] = groups[1]
        else:
          print 'This should not happen'
