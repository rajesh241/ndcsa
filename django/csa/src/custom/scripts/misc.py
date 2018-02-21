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
from django.contrib.auth.models import User
from django.db.models import Count,Sum

from csa.models import Member,Product,OrderForm,ConsolidatedOrderForm,MemberTransaction

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='This Script is for Processing Muster')
  parser.add_argument('-ubid', '--updateBoxID', help='update Box ID', required=False, action='store_const', const=1)
  parser.add_argument('-dzero', '--deleteZeroTransaction', help='deleteZeroTransaction', required=False, action='store_const', const=1)
  parser.add_argument('-cb', '--calculateBalance', help='Calculate Balance', required=False, action='store_const', const=1)
  parser.add_argument('-p', '--print', help='Calculate Balance', required=False, action='store_const', const=1)
  parser.add_argument('-db', '--dumpBalance', help='Dump Balance', required=False, action='store_const', const=1)
  parser.add_argument('-cm', '--changeMemberCode', help='Dump Balance', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-od', '--orderDate', help='Order Date', required=False)
  parser.add_argument('-dt', '--deleteTransactions', help='Delete Transactions', required=False, action='store_const', const=1)
  parser.add_argument('-limit', '--limit', help='Limit on the number of results', required=False)
  parser.add_argument('-id', '--sheetID', help='Limit on the number of results', required=False)

  args = vars(parser.parse_args())
  return args

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  if args['limit']:
    limit = int(args['limit'])
  else:
    limit =1
  if args['changeMemberCode']:
    logger.info("Changing Member Code")
    myUsers=User.objects.all()
    for eachUser in myUsers:
      username=eachUser.username
      areaCode=username[0:2]
      eachMember=Member.objects.filter(user=eachUser).first()
      if eachMember is not None:
        boxID=eachMember.boxID
      else: 
        boxID="abcd"
      boxID=boxID[2:]
      if boxID.isdigit():
        if int(boxID) != 0 and int(boxID) != 1:
          logger.info('username : %s boxID : %s ' % (username,boxID))
          eachUser.username=str(boxID)
          eachUser.save()
      else:
        a=1
#    myMembers=Member.objects.all()[:1]
#    for eachMember in myMembers:
#      logger.info(eachMember.boxID)

  if args['print']:
    orderDateString=args['orderDate']
    orderDate=datetime.strptime(orderDateString, '%d-%m-%Y').date()
    myTransactions=MemberTransaction.objects.filter(orderDate=orderDate).values("member__boxID").annotate(dcount=Count('pk'))
    for eachTransaction in myTransactions:
      logger.info(str(eachTransaction))
      boxID=eachTransaction['member__boxID']
      count=eachTransaction['dcount']
      logger.info(boxID+"-"+str(count))
#    for eachTransaction in myTransactions:
#      logger.info("Prodct: %s Quantity: %s " % (eachTransaction.product.name,str(eachTransaction.quantity)))
  if args['deleteTransactions']:
    orderDateString=args['orderDate']
    orderDate=datetime.strptime(orderDateString, '%d-%m-%Y').date()
    myTransactions=MemberTransaction.objects.filter(orderDate=orderDate)
    for eachTransaction in myTransactions:
      logger.info(eachTransaction.member) 
      eachTransaction.delete()
  if args['dumpBalance']:
    myMembers=Member.objects.all()
    for eachMember in myMembers:
      lastTransaction=MemberTransaction.objects.filter(member=eachMember).order_by("-orderDate","id").first()
      if lastTransaction is not None:
        lastBalance=lastTransaction.balance
      else:
        lastBalance=0
      print(eachMember.user.username+","+str(eachMember.boxID)+",",str(lastBalance))
  if args['calculateBalance']:
   myMembers=Member.objects.all()[:limit]
   for eachMember in myMembers:
     logger.info(eachMember.name)
     memberTransactions=MemberTransaction.objects.filter(member=eachMember).order_by('orderDate','-id')
     curBalance=eachMember.startBalance
     curBalance=0
     logger.info("Current Balance %s " % str(curBalance))
     for eachTransaction in memberTransactions:
       logger.info("%s-%s" % (str(eachTransaction.orderDate),str(eachTransaction.product.name)))
       transactionType=eachTransaction.transactionType
       price=eachTransaction.price
       quantity=eachTransaction.quantity
       if transactionType == "DR":
         amount=price*(-1)*quantity
       else:
         amount=price*1*quantity
#       logger.info("Price : %s, Amount : %s " % (str(price),str(amount)))
       curBalance=curBalance+amount
       eachMember.balance=curBalance
#       logger.info("Current Balance %s " % str(curBalance))
       eachTransaction.balance=curBalance
       eachTransaction.save()       
     eachMember.balance=curBalance
     eachMember.save()
 
  if args['deleteZeroTransaction']:
    myTransactions=MemberTransaction.objects.filter(quantity=0)
    for eachTransaction in myTransactions:
      logger.info(eachTransaction.quantity)
      eachTransaction.delete()

  if args['updateBoxID']:
    logger.info("We are going to update BOx IDs")
      
    with open('/tmp/mm.csv','r') as fp:
       for line in fp:
         line=line.lstrip().rstrip()
         if (line != ''):
           lineArray=str(line).split(",")
           username=lineArray[0]
           boxid=lineArray[1]
           logger.info("Old Username: %s box id %s " % (username,boxid))
           myUser=User.objects.filter(username=username).first()
           myMember=Member.objects.filter(user=myUser).first()
           if myMember is not None:
             print("Member Found")
             myMember.boxID=boxid
             myMember.save()
  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
