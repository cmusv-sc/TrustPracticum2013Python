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


#Just so code is a bit more readable
def strip_quotes(s):
  return re.sub('"','',s)

if __name__ == '__main__':
  db = pymongo.MongoClient()[config.DB_NAME]
  print config.DB_NAME
  doc = {}
  for line in sys.stdin:
    start = re.match('<((article)|(inproceedings)|(proceedings)|(book)|(incollection)|(phdthesis)|(mastersthesis)|(www))',line)
    end = re.match('</((article)|(inproceedings)|(proceedings)|(book)|(incollection)|(phdthesis)|(mastersthesis)|(www))',line)
    if start:
      doc['type'] =  strip_quotes(start.groups()[0])
      tag_attributes = re.findall(' (.+?)=(.+?)(?=[ >])',line)
      for attr in tag_attributes:
        doc[attr[0]] = strip_quotes(attr[1])
      #Sometimes, there's an extra tag on the same line.
      extra_tag = re.match('.+?> <(.+?)>(.+?)</(.+?)>', line)
      if extra_tag:
        groups = extra_tag.groups()
        doc[groups[0]] = strip_quotes(groups[1])
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
          else:
            doc[tag_name] = strip_quotes(tag_info)
        else:
          print 'This should not happen'
