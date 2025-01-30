from import_export import resources, fields
from .models import CustomerModel

class CustomerResource(resources.ModelResource):

    class Meta:
        model = CustomerModel
        # fields=('index','customer_id','first_name','last_name','company','city','country','phone_no1','phone_no2','email','subscription_date','website')
        import_id_fields =('customer_id',)



class CustomerAdminResources(resources.ModelResource):
    
    class Meta:
        model = CustomerModel
        import_id_fields = ['customer_id']
        skip_unchanged = True
        report_skipped = True

    

    