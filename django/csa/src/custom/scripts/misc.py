import datetime
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
  parser.add_argument('-dmonbal', '--dumpMonthlyBalance', help='dumpMonthlyBalance', required=False, action='store_const', const=1)
  parser.add_argument('-montlySpend', '--monthlySpend', help='dumpMonthlyBalance', required=False, action='store_const', const=1)
  parser.add_argument('-memberSpend', '--memberSpend', help='dumpMonthlyBalance', required=False, action='store_const', const=1)
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
  parser.add_argument('-misc', '--misc', help='Do som emisc tasks', required=False,action='store_const', const=1)

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
  if args['misc']:
    logger.info("Doing misc tasks")
    myobjs=MemberTransaction.objects.all()
    for obj in myobjs:
      obj.orderQuantity=obj.quantity
      obj.save()
  if args['memberSpend']:
    logger.info("Member wise spend")
    curmonth=2
    s=""
    myTransactions=MemberTransaction.objects.filter(orderDate__month=curmonth,transactionType='DR')
    for eachTransaction in myTransactions:
      total=str(eachTransaction.price*eachTransaction.quantity)
      s+="%s,%s,%s\n" % (eachTransaction.member.user.username,str(eachTransaction.orderDate),total)
    with open("/tmp/ds.csv","w") as f:
      f.write(s)
    
  if args['monthlySpend']:
    logger.info("Calculating Monthly Spend")
    myMonths=[4,5,6,7,8,9,10,11,12,1,2,3]
    s=''
    for curmonth in myMonths:
      total=0
      myTransactions=MemberTransaction.objects.filter(orderDate__month=curmonth,transactionType='DR')
      for eachTransaction in myTransactions:
        total=total+eachTransaction.price*eachTransaction.quantity
      logger.info(total)
      eachLine="%s,%s\n" % (str(curmonth),str(total))
      s+=eachLine
    with open("/tmp/ms.csv","w") as f:
      f.write(s)
  if args['dumpMonthlyBalance']:
    logger.info("Going to Dump Monthly Balance")
    myMembers=Member.objects.all()
    curmonth=5
    curyear=2018
    s="MemberName,AprilBal,APrilCredit,MayBal,MayCredit,JuneBal,JuneCredit,JulyBal,JulyCredit,AUgustBal,AugustCredit,SeptemberBal,SeptemberCredit,OctoberBal,OctoberCredit,NovemberBal,NovemberCredit,DecemberBal,DecemberCredit,JanuaryBalance,JanuaryCredit,FebuaryBalance,FebuaryCredit\n"
    s="memberCode,memberName,April,May,June,July,August,Sepetember,October,November,December,January,Feb,March\n"
    for eachMember in myMembers:
      s+=str(eachMember.user.username)
      s+=","
      memberID="%s-%s," % (eachMember.user.username,eachMember.name)
      s+=memberID
      curyear=2017
      myMonths=[4,5,6,7,8,9,10,11,12]
      startmonth=5
      startyear=2017
      endmonth=4
      endyear=2018
      myDates=[datetime.date(m//12, m%12+1, 1) for m in range(startyear*12+startmonth-1, endyear*12+endmonth)]
      for eachDate in myDates:
        lastTransaction=MemberTransaction.objects.filter(member=eachMember,orderDate__lt=eachDate).order_by("-orderDate","-id").first()
        if lastTransaction is not None:
          lastBalance=lastTransaction.balance
        else:
          lastBalance=0
        s+=str(lastBalance)
        s+=","
        
#     for curmonth in myMonths:
#       lastTransaction=MemberTransaction.objects.filter(member=eachMember,orderDate__year__lte=curyear,orderDate__month__lte=curmonth).order_by("-orderDate","id").first()
#       if lastTransaction is not None:
#         lastBalance=lastTransaction.balance
#       else:
#         lastBalance=0
#       s+=str(lastBalance)
#       s+=","

#       myTransactions=MemberTransaction.objects.filter(member=eachMember,orderDate__year=curyear,orderDate__month=curmonth,product__id=181)
#       totalCredit=0
#       for eachTransaction in myTransactions:
#         totalCredit+=eachTransaction.price
#       s+=str(totalCredit)
#       s+=","
        
      
#     curyear=2018
#     myMonths=[1,2,3]
#     for curmonth in myMonths:
#       lastTransaction=MemberTransaction.objects.filter(member=eachMember,orderDate__year__lte=curyear,orderDate__month__lte=curmonth).order_by("-orderDate","id").first()
#       if lastTransaction is not None:
#         lastBalance=lastTransaction.balance
#       else:
#         lastBalance=0
#       s+=str(lastBalance)
#       s+=","
#
#       myTransactions=MemberTransaction.objects.filter(member=eachMember,orderDate__year=curyear,orderDate__month=curmonth,product__id=181)
#       totalCredit=0
#       for eachTransaction in myTransactions:
#         totalCredit+=eachTransaction.price
#       s+=str(totalCredit)
#       s+=","
      s+="\n"
    with open("/tmp/mb.csv","w") as f:
      f.write(s)
       
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
    orderDate=datetime.datetime.strptime(orderDateString, '%d-%m-%Y').date()
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
    orderDate=datetime.datetime.strptime(orderDateString, '%d-%m-%Y').date()
    myTransactions=MemberTransaction.objects.filter(orderDate=orderDate)
    for eachTransaction in myTransactions:
      logger.info(eachTransaction.member) 
      eachTransaction.delete()
  if args['dumpBalance']:
    myMembers=Member.objects.all()
    for eachMember in myMembers:
      lastTransaction=MemberTransaction.objects.filter(member=eachMember).order_by("-orderDate","-id").first()
      if lastTransaction is not None:
        lastBalance=lastTransaction.balance
      else:
        lastBalance=0
      print(eachMember.user.username+","+str(eachMember.boxID)+",",str(lastBalance))
  if args['calculateBalance']:
   myMembers=Member.objects.all()[:limit]
   for eachMember in myMembers:
     logger.info(eachMember.name)
     memberTransactions=MemberTransaction.objects.filter(member=eachMember).order_by('orderDate','id')
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
    myTransactions=MemberTransaction.objects.filter(price=0)
    for eachTransaction in myTransactions:
      logger.info(eachTransaction.price)
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
