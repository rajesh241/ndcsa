from datetime import datetime,date
import os
import smtplib
gmail_user = 'navadarshanamcsa.contactus@gmail.com'  
gmail_password = 'csa!2016'
import sys
import re
import time
from customSettings import djangoDir,djangoSettings
from wrappers.logger import loggerFetch
import xlrd
fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.utils import timezone
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from csa.models import Member,Product,OrderForm,ConsolidatedOrderForm,MemberTransaction
from nd_settings import LIBTECH_AWS_ACCESS_KEY_ID,LIBTECH_AWS_SECRET_ACCESS_KEY
from ndcsa.settings import AWS_STORAGE_BUCKET_NAME,AWS_S3_REGION_NAME,MEDIA_URL,S3_URL
import boto3
from boto3.session import Session
from botocore.client import Config
SMTP_INFO = {
    'host': 'smtp.gmail.com',
    'port': 587,
    'username': 'navadarshanamcsa.contactus@gmail.com', # Change this.
    'password': 'csa!2016', # Change this.
}
def argsFetch():
  '''
  Paser for the argument list that returns the args list
  '''
  import argparse

  parser = argparse.ArgumentParser(description='This Script is for Processing Muster')
  parser.add_argument('-u', '--upload', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-sendBalance', '--sendBalance', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-sendOrder', '--sendOrder', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-test', '--test', help='Make the browser visible', required=False, action='store_const', const=1)
  parser.add_argument('-dateFrom', '--dateFrom', help='Log level defining verbosity', required=False)
  parser.add_argument('-dateTo', '--dateTo', help='Log level defining verbosity', required=False)
  parser.add_argument('-l', '--log-level', help='Log level defining verbosity', required=False)
  parser.add_argument('-limit', '--limit', help='Limit on the number of results', required=False)
  parser.add_argument('-id', '--sheetID', help='Limit on the number of results', required=False)

  args = vars(parser.parse_args())
  return args
def genericSendEmail(toEmail,subject,body):
  SENDER_NAME = 'navadarshanam'
  RECIPIENT = 'togoli@gmail.com' # Change this.
  SUBJECT = subject
  BODY_PLAIN_TEXT = 'This is a test.'
  BODY_HTML = body
 
  message = MIMEMultipart('alternative')
  message['From'] = '{} <{}>'.format(SENDER_NAME, SMTP_INFO['username'])
  message['To'] = RECIPIENT
  message['Subject'] = SUBJECT
  # Adding the plain text email body:
  message.attach(MIMEText(BODY_PLAIN_TEXT, 'plain'))
  # Adding the HTML email body:
  message.attach(MIMEText(BODY_HTML, 'html'))
 
# Connecting to the SMTP server:
  with smtplib.SMTP(SMTP_INFO['host'], SMTP_INFO['port']) as smtp:
    # Encrypting the connection:
    smtp.starttls()
    # Logging in and sending the email:
    smtp.login(SMTP_INFO['username'], SMTP_INFO['password'])
    smtp.send_message(message)
def genericSendEmail1(toEmail,subject,body):
  sent_from = gmail_user  
  to=[toEmail,'togoli@gmail.com','sskvsa@gmail.com']
  message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (sent_from, ", ".join(to), subject, body)
  try: 
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(gmail_user, gmail_password)
    server.sendmail(sent_from, to, message)
    server.close()

    print('Email sent!')
  except:  
    print('Something went wrong...')


  
def sendMail(memberEmail,memberName,balance,url,dateString):
  sent_from = gmail_user  
#  to= ['togoli@gmail.com', 'libtech.stanford@gmail.com'] 
  to=[memberEmail,'togoli@gmail.com']
  subject = 'CSA Credit Balance as on %s' % (dateString) 
  body = 'Hey, whats up?\n\n- You'
  firstLine="Dear %s,\n\nYour Navadarshanam CSA credit balance as of %s is Rs.  %s.\n\n Your Detailed account statement can be found here %s \n\n" % (memberName,dateString,str(balance),url )
  ps=''
  secondLine=''
  if balance < 1000:
    secondLine="As you know we request members to add to their credit balance once it goes below Rs. 1000. If you add to your balance, also kindly update your transaction number in the software to enable us track and update your balance. \n\n"
    ps="""

    ********* BANK ACCOUNT DETAILS ***********

    Navadarshanam Trust Self Help Group
    State Bank of India 
    Jaya Nagar 2nd Block Branch
    SB a/c No: 30863225271
    IFSC:SBIN0003286
    Account Type: Savings

    Once the transfer is complete, please do let me know the following details:
    - Bank Name
    - Bank Branch
    - Your phone number
    - Any transaction reference number ?
    """
  lastLine="Thank You. \n On Behalf of Navadarshanam Team \n\n\n"
  body=firstLine+secondLine+lastLine+ps
  email_text = """\  
From: %s \n 
To: %s  \n
Subject: %s\n

%s
""" % (sent_from, ", ".join(to), subject, body)

  message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (sent_from, ", ".join(to), subject, body)
  try: 
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(gmail_user, gmail_password)
    server.sendmail(sent_from, to, message)
    server.close()

    print('Email sent!')
  except:  
    print('Something went wrong...')

def getHTMLHeader():
  header="""
<!DOCTYPE html>
<html lang="en">
<head>
  <title>Navadarshanam CSA</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
</head>
"""
  return header

def main():
  args = argsFetch()
  logger = loggerFetch(args.get('log_level'))
  logger.info('args: %s', str(args))
  logger.info("This is module to Manage Transactions")
  if args['limit']:
    limit = args['limit']
  else:
    limit=50000
  if args['sendOrder']:
    if args['dateFrom']:
      dateFrom=datetime.strptime(args['dateFrom'], '%d-%m-%Y').date()
    if args['dateTo']:
      dateTo=datetime.strptime(args['dateTo'], '%d-%m-%Y').date()
    myMembers=Member.objects.all()[:limit]
    myMembers=Member.objects.filter(user__username="74")
    for eachMember in myMembers:
      if eachMember.user.username.isdigit():
        firstTransaction=MemberTransaction.objects.filter(member=eachMember,orderDate__lte=dateFrom).order_by("-orderDate","-id").first()
        startBalance=firstTransaction.balance
        table=getHTMLHeader()
        table+='<body><table class=" table table-striped" ><tbody>'
        table+="<tr><th>Product</th><th>orderQuantity</th><th>Status</th><th>type</th><th>SuppliedQuantity</th><th>price</th><th>value</th><th>balance</th></tr>"
        tableLine="<tr><td colspan=7>%s</td><td>%s</td></tr>" % ("Start Balance", str(startBalance))
        table+=tableLine
        lastTransaction=MemberTransaction.objects.filter(member=eachMember,orderDate=dateTo).order_by("-id").first()
        lastBalance=lastTransaction.balance
        myTransactions=MemberTransaction.objects.filter(member=eachMember,orderDate__gt=dateFrom,orderDate__lte=dateTo)
        for eachTransaction in myTransactions:
          orderStatus=eachTransaction.orderStatus
          lineValue=eachTransaction.price*eachTransaction.quantity
          tableLine="<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (eachTransaction.product.name,str(eachTransaction.orderQuantity),orderStatus,eachTransaction.transactionType,str(eachTransaction.quantity),str(eachTransaction.price),str(lineValue),str(eachTransaction.balance)) 
          table+=tableLine
        tableLine="<tr><td colspan=7>%s</td><td>%s</td></tr>" % ("Last Balance", str(lastBalance))
        table+=tableLine
        table+='</tbody></table ></body>'
        toEmail="libtech.stanford@gmail.com"
        body=table
        subject="In Todays Box"
        with open("/tmp/aaa.html","w") as f:
          f.write(table)
        genericSendEmail(toEmail,subject,body)
  if args['sendBalance']:
    d=date.today()
    dateString=str(datetime.strftime(d, "%b-%d"))
    baseURL="https://s3.ap-south-1.amazonaws.com/ndcsa/memberData/"
    logger.info("Sending the balance")
    myMembers=Member.objects.filter(isActive=True)[:limit]
    for eachMember in myMembers:
      if eachMember.user.username.isdigit():
        lastTransaction=MemberTransaction.objects.filter(member=eachMember).order_by("-orderDate","-id").first()
        if lastTransaction is not None:
          lastBalance=lastTransaction.balance
          logger.info("%s-%s-%s" % (str(eachMember.user.username),eachMember.name,str(lastBalance)))
          balanceURL="%s%s.csv" % (baseURL,str(eachMember.user.username))
          logger.info(balanceURL)
          memberEmail=eachMember.user.email
          if args['test']:
            memberEmail="togoli@gmail.com"
          logger.info(memberEmail)
          sendMail(memberEmail,eachMember.name,lastBalance,balanceURL,dateString)
  if args['upload']:
    logger.info("Will upload everyone transaction History")
    myMembers=Member.objects.all()[:limit]
    for eachMember in myMembers:
      logger.info(eachMember.user.username)
      logger.info(eachMember.name)
      memID=str(eachMember.user.username)+"-"+eachMember.name
      s=''
      balance=0
      s+="member,orderDate,product,quantity,price,total,type,balance\n"
      myTransactions=MemberTransaction.objects.filter(member=eachMember).order_by("orderDate","id")
      for eachTransaction in myTransactions:
        logger.info(eachTransaction.product.name)
        logger.info(eachTransaction.orderDate)
        total=eachTransaction.quantity*eachTransaction.price
        if eachTransaction.transactionType == 'DR':
          balance=balance-total
        else:
          balance=balance+total
        s+="%s,%s,%s,%s,%s,%s,%s,%s\n" % (memID,str(eachTransaction.orderDate),eachTransaction.product.name,str(eachTransaction.quantity),str(eachTransaction.price),str(total),eachTransaction.transactionType,str(balance))
      logger.info(s)
       
      cloudFilename="memberData/%s.csv" % (str(eachMember.user.username))
      session = boto3.session.Session(aws_access_key_id=LIBTECH_AWS_ACCESS_KEY_ID,
                                      aws_secret_access_key=LIBTECH_AWS_SECRET_ACCESS_KEY)
      s3 = session.resource('s3',config=Config(signature_version='s3v4'))
      s3.Bucket(AWS_STORAGE_BUCKET_NAME).put_object(ACL='public-read',Key=cloudFilename, Body=s)
  logger.info("...END PROCESSING") 
  exit(0)
if __name__ == '__main__':
  main()
