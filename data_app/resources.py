from import_export import resources, fields
from .models import CustomerModel


class CustomerResource(resources.ModelResource):

    index = fields.Field(attribute='index',column_name='Index')
    customer_id = fields.Field(attribute='customer_id', column_name='Customer Id')
    first_name = fields.Field(attribute='first_name', column_name='First Name')
    last_name = fields.Field(attribute='last_name', column_name='Last Name')
    company = fields.Field(attribute='company', column_name='Company')
    city = fields.Field(attribute='city', column_name='City')
    country = fields.Field(attribute='country', column_name='Country')
    phone_no1 = fields.Field(attribute='phone_no1', column_name='Phone 1')
    phone_no2 = fields.Field(attribute='phone_no2', column_name='Phone 2')
    email = fields.Field(attribute='email', column_name='Email')
    subscription_date = fields.Field(attribute='subscription_date', column_name='Subscription Date')
    website = fields.Field(attribute='website', column_name='Website')

    class Meta:
        model = CustomerModel
        fields=('index','customer_id','first_name','last_name','company','city','country','phone_no1','phone_no2','email','subscription_date','website')
        import_id_fields =('customer_id',)

