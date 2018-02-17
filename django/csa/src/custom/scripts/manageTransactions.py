from datetime import datetime,date
import os
import sys
import re
import time
from customSettings import djangoDir,djangoSettings
from wrappers.logger import loggerFetch
import xlrd
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)


import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.utils import timezone
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from csa.models import Member,Product,OrderForm,ConsolidatedOrderForm,MemberTransaction

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='This Script is for Processing Muster')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit on the number of results', required=False)
  parser.add_argument('-id', '--sheetID', help='Limit on the number of results', required=False)

  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  logger.info("This is module to Manage Transactions")


  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
