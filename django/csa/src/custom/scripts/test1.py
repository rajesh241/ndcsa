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
from django.contrib.auth.models import User

from csa.models import Member

with open('/tmp/allMembers4.csv','rb') as fp:
    for line in fp:
      try:
        line=line.decode("UTF-8")
      except:
        line=line
      line=line.lstrip().rstrip()
      if (line != '') and ('ID' not in line):
        lineArray=str(line).split(",")
        code=lineArray[1]
        email=lineArray[5]
        print(code+email)
        myUser=User.objects.filter(username=code).first()
        if myUser is None:
          print("User does not exists")
          User.objects.create(username=code,email=email,password=code)
        myUser=User.objects.filter(username=code).first()
        myMember=Member.objects.filter(user=myUser).first()
        if myMember is not None:
          print("Member Found")
        else:
          myMember=Member.objects.create(user=myUser)
        myMember=Member.objects.filter(user=myUser).first()
        myMember.areaCode=lineArray[3].lstrip().rstrip()
        print(myMember.areaCode)
        myMember.name=lineArray[0].lstrip().rstrip()
        myMember.phone=lineArray[6].lstrip().rstrip()
        myMember.exclusions=lineArray[9].lstrip().rstrip()
        if lineArray[2].lstrip().rstrip() == 'no':
          myMember.isActive=False
        myMember.save()
       #if myMember is None:
       #   Member.objects.create(code=code)
       #myMember=Member.objects.filter(code=code).first()
       #myMember.name=name
       #myMember.areaCode=code[0:2]
       #myMember.save()
       #print(code)

