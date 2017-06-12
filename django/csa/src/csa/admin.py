from django.contrib import admin
from .models import Member,Product
# Register your models here.

class memberModelAdmin(admin.ModelAdmin):
  list_display = ["name","get_code","isActive","areaCode","phone","get_email"]
  search_fields=["name","user__username"]
  list_filter=["isActive","areaCode"] 
  def get_code(self,obj):
    return obj.user.username
  get_code.description="Member ID"
  def get_email(self,obj):
    return obj.user.email
  get_email.description="Email"
 
 
class productModelAdmin(admin.ModelAdmin):
  list_display = ["name","code","price"]
  search_fields=["name"]
admin.site.register(Member,memberModelAdmin)
admin.site.register(Product,productModelAdmin)
