#!/usr/bin/env python

import config
from ml.scratch import *

import sys

if __name__ == '__main__':
  db = pymongo.MongoClient()[config.DB_NAME]
  col = db[config.COLLECTION_NAME]
  lst = []
  if len(sys.argv) == 2:
    year = int(sys.argv[1])
  else:
    year = 2014
  for name in sys.stdin:
    lst.append(name)
  for n1 in lst:
    for n2 in lst:
      if n1 != n2:
        print write_line_for_authors(col, n1, n2, year)
