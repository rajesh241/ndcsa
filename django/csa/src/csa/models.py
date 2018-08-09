from django.db import models
import xlrd
import datetime
import os
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import pre_save,post_save
from django.utils.text import slugify
# Create your models here.
def get_orderform_upload_path(instance, filename):
  return os.path.join(
    "csa","orderForms",instance.member.user.username,filename)
def get_invoiceform_upload_path(instance, filename):
  filename=slugify(filename)
  return os.path.join(
    "shg","invoicesSRN",instance.finyear,filename)

def get_consolidatedorderform_upload_path(instance, filename):
  return os.path.join(
    "csa","orderForms","consolidated",filename)

class Member(models.Model):
  Box_Choices = (
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
    )
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  name=models.CharField(max_length=512,blank=True,null=True)
  slug=models.SlugField(blank=True) 
  areaCode=models.CharField(max_length=2,blank=True,null=True)
  isActive=models.BooleanField(default=True)
  boxSize=models.CharField(max_length=2,choices=Box_Choices,null=True,blank=True)
  phone=models.CharField(max_length=512,blank=True,null=True) 
  boxID=models.CharField(max_length=10,blank=True,null=True) 
  exclusions=models.CharField(max_length=512,blank=True,null=True) 
  startBalance=models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
  balance=models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
  
  def __str__(self):
    return self.user.username
class Customer(models.Model):
  name=models.CharField(max_length=512)
  slug=models.SlugField(blank=True) 
  code=models.CharField(max_length=16,blank=True,null=True)
  pincode=models.CharField(max_length=10,null=True,blank=True)
  gst=models.CharField(max_length=16,null=True,blank=True)
  route=models.CharField(max_length=4,null=True,blank=True)
  phone=models.CharField(max_length=10,null=True,blank=True)
  address=models.CharField(max_length=1024,null=True,blank=True)
  email=models.CharField(max_length=256,null=True,blank=True)
  distance=models.PositiveSmallIntegerField(null=True,blank=True,default=60)
  def __str__(self):
    return self.name
   
class Product(models.Model):
  name=models.CharField(max_length=512)
  slug=models.SlugField(blank=True) 
  code=models.CharField(max_length=16,blank=True,null=True)
  price=models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
  def __str__(self):
    return self.name

class OrderForm(models.Model):
  member=models.ForeignKey('Member')
  orderFile=models.FileField(upload_to=get_orderform_upload_path,max_length=512)
  orderDate=models.DateField()
  isProcessed=models.BooleanField(default=False)
  class Meta:
        unique_together = ('member', 'orderDate')  
  def __str__(self):
    return self.member.user.username+" "+" "+self.member.name+" "+str(self.orderDate)

class InvoiceSRN(models.Model):
  Invoice_Types = (
        ('TN', 'Tamil Nadu'),
        ('RI', 'Rest Of India'),
    )
  Document_Types = (
        ('INV', 'Invoice'),
        ('SRN', 'SalesReturn'),
    )
  documentNo=models.CharField(max_length=16)
  customer=models.ForeignKey('Customer')
  filename=models.FileField(upload_to=get_invoiceform_upload_path,max_length=512)
  region=models.CharField(max_length=2,choices=Invoice_Types,default='RI',null=True,blank=True)
  documentType=models.CharField(max_length=3,choices=Document_Types,default='INV',null=True,blank=True)
  finyear=models.CharField(max_length=16,default="1819")
  orderDate=models.DateField()
  def __str__(self):
    if self.customer:
      custname=self.customer.slug
    else:
      custname=''
    return "%s_%s_%s" % (self.documentNo,custname,str(self.orderDate))

class ConsolidatedOrderForm(models.Model):
  orderFile=models.FileField(upload_to=get_consolidatedorderform_upload_path,max_length=512)
  orderDate=models.DateField(unique=True)
  sheetNo=models.PositiveSmallIntegerField(default=4)
  balanceSheetIndex=models.PositiveSmallIntegerField(default=10)
  creditSheetIndex=models.PositiveSmallIntegerField(default=5)
  isItemizedOrderFormat=models.BooleanField(default=True)
  maxRow=models.PositiveSmallIntegerField(default=95)
  creditIndex=models.PositiveSmallIntegerField(default=0)
  isProcessed=models.BooleanField(default=False)
  def __str__(self):
    return "Consolidated Order "+str(self.orderDate)

class CustomerProduct(models.Model):
  Transaction_Choices = (
        ('CR', 'Credit'),
        ('DR', 'Debit'),
    )
  name=models.CharField(max_length=64,blank=True,null=True)
  transactionType=models.CharField(max_length=2,choices=Transaction_Choices,default='CR')
  def __str__(self):
    return self.name

class CustomerTransaction(models.Model):
  Document_Types = (
        ('INV', 'Invoice'),
        ('SRN', 'SalesReturn'),
        ('CDT', 'Credit'),
        ('ADT', 'Adjustment'),
        ('OPB', 'OpeningBalance'),
    )
  Transaction_Choices = (
        ('CR', 'Credit'),
        ('DR', 'Debit'),
    )
  customer=models.ForeignKey('Customer')
  #customerProduct=models.ForeignKey('CustomerProduct')
  finyear=models.CharField(max_length=16,default="1819")
  orderDate=models.DateField()
  docNo=models.CharField(max_length=64,blank=True,null=True)
  documentType=models.CharField(max_length=3,choices=Document_Types,default='INV',null=True,blank=True)
  filename=models.FileField(null=True,blank=True,upload_to=get_invoiceform_upload_path,max_length=512)
  value=models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
  transactionType=models.CharField(max_length=2,choices=Transaction_Choices,default='CR')
  balance=models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
  def __str__(self):
    return "%s-%s" % (self.customer.slug,str(self.value)) 

class CustomerOrderDetails(models.Model):
  customer=models.ForeignKey('Customer')
  product=models.ForeignKey('Product')
  invoice=models.ForeignKey('InvoiceSRN')
  price=models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
  quantity=models.DecimalField(max_digits=10,decimal_places=2,default=1)
  
class MemberTransaction(models.Model):
  Transaction_Choices = (
        ('CR', 'Credit'),
        ('DR', 'Debit'),
    )
  OrderStatus_Choices =(
        ('CAN', 'Cancelled'),
        ('MOD', 'Modified'),
        ('FUL', 'Fulfilled'),
    )
     
  member=models.ForeignKey('Member')
  product=models.ForeignKey('Product')
  orderDate=models.DateField()
  transactionType=models.CharField(max_length=2,choices=Transaction_Choices,default='CR')
  price=models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
  quantity=models.DecimalField(max_digits=10,decimal_places=2,default=1)
  orderQuantity=models.DecimalField(max_digits=10,decimal_places=2,default=1,null=True,blank=True)
  balance=models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
  remarks=models.CharField(max_length=256,blank=True,null=True)
  orderStatus=models.CharField(max_length=3,choices=OrderStatus_Choices,default='FUL',blank=True,null=True)
  
  def __str__(self):
    return "%s-%s" % (self.member.user.username,self.member.name)
  
  def getProductName(self):
    return self.product.name  

  def getTotalValue(self):
    try:
      return int(self.quantity*self.price)
    except:
      return 0
  
class DateLookup(models.Model):
  dateString=models.CharField(max_length=16)
  dateObject=models.DateField()
  def __str__(self):
    return self.dateString

def createslug(instance):
  myslug=slugify(instance.name)[:50]
  if myslug == '':
    myslug="%s-%s" % (instance.__class__.__name__ , str(instance.id))
  return myslug

def customerTransaction_post_save_receiver(sender,instance,*args,**kwargs):
  documentType=instance.documentType
  if instance.value is None:
    if documentType == "INV" or documentType=="SRN":
      transactionType="DR"
      if documentType =="SRN":
        transactionType="CR"
      totalValue=getInvoiceValue(instance)
      instance.value=totalValue
      instance.transactionType=transactionType
    else:
      instance.value=0
    instance.save()
#  if instance.balance is None:
#    customerID=instance.customer.id
#    calculateCustomerBalance(customerID)
   
#  calculateCustomerBalance(customerID)
# documentType=instance.documentType
# if documentType == "INV":
#   totalValue=getInvoiceValue(instance)
#   transactionType="DR"
#   instance.transactionType=transactionType
#   instance.totalValue=totalValue
#   instance.save()
# elif documentType == "SRN":
#   transactionType="CR"
#   totalValue=getInvoiceValue(instance)
#   instance.transactionType=transactionType
#   instance.totalValue=totalValue
#   instance.save()
 
def name_post_save_receiver(sender,instance,*args,**kwargs):
  myslug=createslug(instance)
  if instance.slug != myslug:
    instance.slug = myslug
    instance.save()
#  print(instance.__class__.__name__)

# def transaction_post_save_receiver(sender,instance,*args,**kwargs):
# myMember=instance.member
# startBalance=instance.member.startBalance
# balance=startBalance
#   
# if instance.balance != balance:
#   instance.balance=balance 
#   instance.save()

#post_save.connect(transaction_post_save_receiver,sender=MemberTransaction)
post_save.connect(name_post_save_receiver,sender=Member)
post_save.connect(name_post_save_receiver,sender=Product) 
post_save.connect(name_post_save_receiver,sender=Customer) 
#post_save.connect(invoice_post_save_receiver,sender=InvoiceSRN)
post_save.connect(customerTransaction_post_save_receiver,sender=CustomerTransaction)

def getInvoiceValue(eachInvoice):
#  print("Going to get invoice value")
  invoiceValue = 100
  myFile=eachInvoice.filename.read()
  book = xlrd.open_workbook(file_contents=myFile)
  worksheet = book.sheet_by_index(0)
  num_rows=worksheet.nrows-1
  i=num_rows
  while i > 0:
    row = worksheet.row(i)
    if "TOTAL :ROUNDED OFF" in str(row):
 #     print(row)
      j=0
      while j < 14:
        cellType=worksheet.cell_type(i,j) 
        if cellType == 2:
          invoiceValue=worksheet.cell_value(i,j)
#        print(cellType)
        j=j+1
    i=i-1
  return invoiceValue

def calculateCustomerBalance(custID=None):
  if custID is not None:
    myCustomers=Customer.objects.filter(id=custID)
  else:
    myCustomers=Customer.objects.all()
  for eachCustomer in myCustomers:
    myTransactions=CustomerTransaction.objects.filter(customer=eachCustomer).order_by("orderDate","id")
    balance=0
    for eachTransaction in myTransactions:
      if eachTransaction.value is not None:
        transactionType=eachTransaction.transactionType
        if transactionType == "DR":
          balance=balance-eachTransaction.value
        else:
          balance=balance+eachTransaction.value
      eachTransaction.balance=balance
      eachTransaction.save()
    print(eachCustomer.name)
