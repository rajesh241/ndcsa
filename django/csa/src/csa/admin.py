from django.contrib import admin
from .models import Member,Product,OrderForm,DateLookup,ConsolidatedOrderForm,MemberTransaction
from .actions import export_as_csv_action
# Register your models here.

#from .actions import calculateBalance

class memberModelAdmin(admin.ModelAdmin):
#  actions = [calculateBalance("Calculate Balance", fields=['name'])]
  list_display = ["get_code","balance","name","isActive","boxSize","areaCode","phone","get_email"]
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

class orderformModelAdmin(admin.ModelAdmin):
  list_display=["__str__","orderDate"]

class consolidatedOrderFormModelAdmin(admin.ModelAdmin):
  list_display=["__str__"]

class dateLookupModelAdmin(admin.ModelAdmin):
  list_display=["dateString","dateObject"]

class memberTransactionModelAdmin(admin.ModelAdmin):
  actions = [export_as_csv_action("CSV Export", fields=['__str__','orderDate','getProductName','quantity','price','getTotalValue','remarks','transactionType','balance'])]
  list_display=["__str__","orderDate","getProductName","quantity","price","getTotalValue","remarks","transactionType","balance"]
  list_filter=["transactionType","orderDate","member__user__username"]
  search_fields=["member__user__username","product__name"]
  readonly_fields=["balance"]
#  def getProductName(self,obj):
 #   return obj.product.name
  
admin.site.register(MemberTransaction,memberTransactionModelAdmin)
admin.site.register(ConsolidatedOrderForm,consolidatedOrderFormModelAdmin)
admin.site.register(DateLookup,dateLookupModelAdmin)
admin.site.register(Member,memberModelAdmin)
admin.site.register(Product,productModelAdmin)
admin.site.register(OrderForm,orderformModelAdmin)
