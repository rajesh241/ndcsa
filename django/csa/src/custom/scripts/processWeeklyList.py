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
from csa.models import Member,Product,OrderForm,ConsolidatedOrderForm,MemberTransaction

def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='This Script is for Processing Muster')
  parser.add_argument('-v', '--visible', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit on the number of results', required=False)
  parser.add_argument('-id', '--sheetID', help='Limit on the number of results', required=False)

  args = vars(parser.parse_args())
  return args

def addMemberTransaction(logger,myMember,productCode,productQuantity,productPrice,transactionType,orderDate,orderStatus=None,remarks=None):
  error = None
  myProduct=Product.objects.filter(code=productCode).first()
  quantity=productQuantity
  if orderStatus is not None:
    if orderStatus=="CAN":
       quantity=0
  if orderStatus is None:
    orderStatus="FUL"
  if myProduct is None:
    error="Product not Found"
    logger.info("Product %s not found " % (productCode))
  else:
    myMemberTransaction=MemberTransaction.objects.filter(member=myMember,product=myProduct,orderDate=orderDate).first()
    if myMemberTransaction is None:
      MemberTransaction.objects.create(member=myMember,product=myProduct,orderDate=orderDate)
    myMemberTransaction=MemberTransaction.objects.filter(member=myMember,product=myProduct,orderDate=orderDate).first()
    myMemberTransaction.orderQuantity=productQuantity
    myMemberTransaction.quantity=quantity
    myMember.orderStatus=orderStatus
    myMemberTransaction.transactionType=transactionType
    myMemberTransaction.price=productPrice
    myMemberTransaction.remarks=remarks
    myMemberTransaction.save()
  return error

def main():
  thresholdDate=datetime.strptime('Oct 15 2017', '%b %d %Y').date()
  memberIndex=1
  productNameIndex=0
  startCol=6
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  print("test")
  if args['limit']:
    limit = int(args['limit'])
  else:
    limit =1
 
  #Lets Process Grocery Order Form
  if args['sheetID']:
    myOrderForms=ConsolidatedOrderForm.objects.filter(isProcessed=0,id=args['sheetID'])[:limit]
  else:
    myOrderForms=ConsolidatedOrderForm.objects.filter(isProcessed=0)[:limit]
  for eachOrderForm in myOrderForms:
    isBeforeSoftware=False
    productCodeIndex=2
    priceIndex=4
    orderDate=eachOrderForm.orderDate
    if orderDate < thresholdDate:
      isBeforeSoftware=True
      productCodeIndex=1
      priceIndex=2
    creditIndex=eachOrderForm.creditIndex-1
    creditSheetIndex=eachOrderForm.creditSheetIndex
    sheetIndex=eachOrderForm.sheetNo
    balanceSheetIndex=eachOrderForm.balanceSheetIndex
    maxOrderRow=eachOrderForm.maxRow
    myFile=eachOrderForm.orderFile.read()
    book = xlrd.open_workbook(file_contents=myFile)
    #Balance Sheet Index
    worksheet = book.sheet_by_index(balanceSheetIndex)
    num_rows=worksheet.nrows-1
    curr_row=0
    vegetableCostIndex=11
    creditIndex=10
    adjustmentIndex=11
    adjustmentReasonIndex=14
    nameIndex=4
    emailIndex=5
    boxIDIndex=1 
    password="nregapds!"
    while curr_row < num_rows:
      curr_row=curr_row+1
      memberCode=str(worksheet.cell_value(curr_row,0)).replace("-","").lstrip().rstrip()
      vegetableCost=int(worksheet.cell_value(curr_row,vegetableCostIndex))

      if isBeforeSoftware==True:
        memberCode=str(worksheet.cell_value(curr_row,0)).replace("-","").lstrip().rstrip()
        myMember=Member.objects.filter(user__username=memberCode).first()
      else:
        memberCode=int(worksheet.cell_value(curr_row,0))
        if memberCode != 0:
          boxID=str(worksheet.cell_value(curr_row,boxIDIndex)).lstrip().rstrip()
          email=str(worksheet.cell_value(curr_row,emailIndex)).lstrip().rstrip()
          name=str(worksheet.cell_value(curr_row,nameIndex)).lstrip().rstrip()
          myMember=Member.objects.filter(user__username=memberCode).first()
          logger.info(str(int(memberCode)))
          if myMember is None:
            myUser=User.objects.create_user(username=memberCode,email=email,password=password)
            Member.objects.create(user=myUser,boxID=boxID,name=name)
          else:
            myUser=myMember.user
            myUser.email=email
            myUser.save()
          myMember=Member.objects.filter(user__username=memberCode).first()
        #myMember=Member.objects.filter(boxID=memberCode).first()

      if myMember is None:
        allMembersFound=0
        logger.info("Member not found %s " % (memberCode))
      else:
        if vegetableCost != 0:
          error=addMemberTransaction(logger,myMember,"VEGBOX",1,vegetableCost,"DR",orderDate)
        #Making the credit and Adjustment
        if isBeforeSoftware==True:
          if worksheet.cell_type(curr_row,creditIndex) != 0:
            credit=str(worksheet.cell_value(curr_row,creditIndex)).replace("-","").lstrip().rstrip()
            error=addMemberTransaction(logger,myMember,"CRR",1,credit,"CR",orderDate)
          if worksheet.cell_type(curr_row,adjustmentIndex) != 0:
            adjustment=str(worksheet.cell_value(curr_row,adjustmentIndex)).lstrip().rstrip()
            logger.info(adjustment)
            adjustmentReason=str(worksheet.cell_value(curr_row,adjustmentReasonIndex)).replace("-","").lstrip().rstrip()
            if "-" in adjustment:
              logger.info("Adjustment is Negative")
              adjustmentTransactionType="CR"
              adjustment=adjustment[1:]
            else:
              adjustmentTransactionType="DR"
            error=addMemberTransaction(logger,myMember,"ADJST",1,adjustment,adjustmentTransactionType,orderDate,remarks=adjustmentReason)
#This is for calcuating Credits
    if creditSheetIndex != 0:
      worksheet = book.sheet_by_index(creditSheetIndex)
      num_cols=worksheet.ncols-1
      num_rows=worksheet.nrows-1
      curr_row=0
      while curr_row < num_rows:
        curr_row +=1
        memberCode=int(worksheet.cell_value(curr_row,0))
        logger.info("Credit memberCode %s " % str(memberCode))
        Amount=worksheet.cell_value(curr_row,1)
        creditDateExcel=worksheet.cell_value(curr_row,2)
        creditDate = datetime(*xlrd.xldate_as_tuple(creditDateExcel, 0)).date()
        logger.info(str(memberCode)+str(Amount)+str(creditDate))
        myMember=Member.objects.filter(user__username=memberCode).first()
        if myMember is not None:
          error=addMemberTransaction(logger,myMember,"CRR",1,Amount,"CR",creditDate)
#This is for calculating Products
    if eachOrderForm.isItemizedOrderFormat == False:
      worksheet = book.sheet_by_index(sheetIndex)
      isComplete=1
      firstRow=worksheet.row_values(0)
      logger.info(str(firstRow))
      num_cols = worksheet.ncols - 1
      curr_col = startCol
      allMembersFound=1
      while curr_col < num_cols:
        curr_col +=1
        if worksheet.cell_type(memberIndex,curr_col) != 0:
          memberCode=str(worksheet.cell_value(memberIndex,curr_col)).replace("-","")
          memberCode=memberCode[2:]
        #  logger.info(memberCode)
          if isBeforeSoftware==True:
            myMember=Member.objects.filter(user__username=memberCode).first()
          else:
            myMember=Member.objects.filter(user__username=memberCode).first()
            #myMember=Member.objects.filter(boxID=memberCode).first()

          if myMember is None:
            allMembersFound=0
            logger.info("Member not found %s " % (memberCode))
          else:
            curr_row= 2
            while curr_row < maxOrderRow:
              curr_row+=1
              if worksheet.cell_type(curr_row,curr_col) != 0:
                 if worksheet.cell_type(curr_row,priceIndex) != 0:
                   productName=worksheet.cell_value(curr_row,productNameIndex).lstrip().rstrip()
                   productCode=worksheet.cell_value(curr_row,productCodeIndex).lstrip().rstrip()
                   price=worksheet.cell_value(curr_row,priceIndex)
                   quantity=worksheet.cell_value(curr_row,curr_col)
                   if float(quantity) != 0:
                     logger.info("Product Code: %s Price : %s Quantity %s Member %s " % (productCode,price,str(int(quantity)),memberCode))
                     error=addMemberTransaction(logger,myMember,productCode,quantity,price,"DR",orderDate)
                     if error is not None:
                       isComplete=False
    else:
      logger.info("I am in itemized biling")
      productCodeIndex=15
      priceIndex=12
      quantityIndex=11
      orderStatusIndex=19
      worksheet = book.sheet_by_index(sheetIndex)
      isComplete=1
      num_rows = worksheet.nrows - 1
      num_cols = worksheet.ncols - 1
      curr_col = startCol
      allMembersFound=1
      row = 0
      while row < num_rows: 
        row=row+1
        rowValues=worksheet.row_values(row)
#        logger.info(str(rowValues))
        logger.info(row)
        logger.info(worksheet.cell_value(row,1))
        memberCode=int(worksheet.cell_value(row,1))
        myMember=Member.objects.filter(user__username=memberCode).first()
        productCode=worksheet.cell_value(row,productCodeIndex).lstrip().rstrip()
        orderStatus=worksheet.cell_value(row,orderStatusIndex).lstrip().rstrip()
        quantity=worksheet.cell_value(row,quantityIndex)
        price=worksheet.cell_value(row,priceIndex)
        error=addMemberTransaction(logger,myMember,productCode,quantity,price,"DR",orderDate,orderStatus=orderStatus)

    if (isComplete == True) and (allMembersFound == 1):
      logger.info("Sheet is Completely Processed")
      
        


  logger.info("...END PROCESSING") 
  exit(0)

if __name__ == '__main__':
  main()
