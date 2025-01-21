from django.contrib import admin
from .models import CustomerModel
# from import_export.admin import ImportExportModelAdmin
# from .resources import CustomerResource

# @admin.register(CustomerModel)
# class CustomerAdmin(ImportExportModelAdmin):

#     resource_class= CustomerResource
#     list_display=('index','customer_id','first_name','last_name','company','city','country','phone_no1','phone_no2','email','subscription_date','website')



#  register customer model here 

@admin.register(CustomerModel)

class CustomerAdmin(admin.ModelAdmin):
    list_display=('index','customer_id','first_name','last_name','company','city','country','phone_no1','phone_no2','email','subscription_date','website')