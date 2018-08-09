from django.contrib import admin
from .models import Member,Product,OrderForm,DateLookup,ConsolidatedOrderForm,MemberTransaction,InvoiceSRN,Customer,CustomerProduct,CustomerTransaction
from .actions import export_as_csv_action,get_eway_dump,cancelMemberTransactions,makeMemberInactive
# Register your models here.

#from .actions import calculateBalance

class memberModelAdmin(admin.ModelAdmin):
  actions = [makeMemberInactive]
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
 
class customerProductModelAdmin(admin.ModelAdmin):
  list_display=["name"]

class customerTransactionModelAdmin(admin.ModelAdmin):
  actions = [get_eway_dump]
  list_display=["customer","value","documentType","orderDate","docNo","transactionType","balance"]
  list_filter=["customer__name"] 
class productModelAdmin(admin.ModelAdmin):
  list_display = ["name","code","price"]
  search_fields=["name"]

class customerModelAdmin(admin.ModelAdmin):
   actions = [cancelMemberTransactions,export_as_csv_action("CSV Export", fields=['id','name'])]
   list_display =["name","code","pincode","gst"]
   search_fields=['name']

class orderformModelAdmin(admin.ModelAdmin):
  list_display=["__str__","orderDate"]

class consolidatedOrderFormModelAdmin(admin.ModelAdmin):
  list_display=["__str__"]

class invoiceModelAdmin(admin.ModelAdmin):
  actions = [get_eway_dump]
  list_display=["__str__"]

class dateLookupModelAdmin(admin.ModelAdmin):
  list_display=["dateString","dateObject"]

class memberTransactionModelAdmin(admin.ModelAdmin):
  actions = [cancelMemberTransactions,export_as_csv_action("CSV Export", fields=['__str__','orderDate','getProductName','quantity','price','getTotalValue','remarks','transactionType','balance'])]
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
#admin.site.register(InvoiceSRN,invoiceModelAdmin)
admin.site.register(Customer,customerModelAdmin)
admin.site.register(CustomerProduct,customerProductModelAdmin)
admin.site.register(CustomerTransaction,customerTransactionModelAdmin)
