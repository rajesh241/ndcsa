from django.db import models

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


class ConsolidatedOrderForm(models.Model):
  orderFile=models.FileField(upload_to=get_consolidatedorderform_upload_path,max_length=512)
  orderDate=models.DateField(unique=True)
  sheetNo=models.PositiveSmallIntegerField()
  balanceSheetIndex=models.PositiveSmallIntegerField(default=0)
  creditSheetIndex=models.PositiveSmallIntegerField(default=0)
  maxRow=models.PositiveSmallIntegerField()
  creditIndex=models.PositiveSmallIntegerField()
  isProcessed=models.BooleanField(default=False)
  def __str__(self):
    return "Consolidated Order "+str(self.orderDate)

class MemberTransaction(models.Model):
  Transaction_Choices = (
        ('CR', 'Credit'),
        ('DR', 'Debit'),
    )
  member=models.ForeignKey('Member')
  product=models.ForeignKey('Product')
  orderDate=models.DateField()
  transactionType=models.CharField(max_length=2,choices=Transaction_Choices,default='CR')
  price=models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
  quantity=models.DecimalField(max_digits=10,decimal_places=2,default=1)
  balance=models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
  remarks=models.CharField(max_length=256,blank=True,null=True)
  
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
