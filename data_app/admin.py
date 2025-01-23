from django.contrib import admin
from .models import CustomerModel
from import_export.admin import ImportExportModelAdmin
from .resources import CustomerAdminResources



class CustomerAdmin(ImportExportModelAdmin):
    resource_class= CustomerAdminResources
admin.site.register(CustomerModel,CustomerAdmin)

# class CustomerAdmin(admin.ModelAdmin):
#     list_display=('index','customer_id','first_name','last_name','company','city','country','phone_no1','phone_no2','email','subscription_date','website')


class customAdmin(ImportExportModelAdmin):
    resource_class= CustomerAdminResources
    