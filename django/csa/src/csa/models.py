from django.db import models

import datetime
import os
from django.utils import timezone
from django.contrib.auth.models import User
# Create your models here.
class Member(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  name=models.CharField(max_length=512,blank=True,null=True)
  areaCode=models.CharField(max_length=2,blank=True,null=True)
  isActive=models.BooleanField(default=True)
  phone=models.CharField(max_length=512,blank=True,null=True) 
  exclusions=models.CharField(max_length=512,blank=True,null=True) 
  def __str__(self):
    return self.user.username
 
class Product(models.Model):
  name=models.CharField(max_length=512)
  code=models.CharField(max_length=6,unique=True)
  price=models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
  
  def __str__(self):
    return self.name
