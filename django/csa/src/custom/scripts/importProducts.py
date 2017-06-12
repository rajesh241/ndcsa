from datetime import datetime,date
import os
import sys
import re
import time
from customSettings import djangoDir,djangoSettings

fileDir=os.path.dirname(os.path.abspath(__file__))
sys.path.append(djangoDir)


import django
from django.core.wsgi import get_wsgi_application
from django.core.files.base import ContentFile
from django.utils import timezone
os.environ.setdefault("DJANGO_SETTINGS_MODULE", djangoSettings)
django.setup()

from csa.models import Member


with open('/tmp/products.csv','rb') as fp:
    for line in fp:
      try:
        line=line.decode("UTF-8")
      except:
        line=line
      line=line.lstrip().rstrip()
      if line != '':
        lineArray=str(line).split(",")
        code=lineArray[1]
        name=lineArray[0]
        myMember=Member.objects.filter(code=code).first()
        if myMember is None:
           Member.objects.create(code=code)
        myMember=Member.objects.filter(code=code).first()
        myMember.name=name
        myMember.areaCode=code[0:2]
        myMember.save()
        print(code)


