from django.db import models

# Create your models here.

class CustomerModel(models.Model):
    index = models.IntegerField(default=0)
    customer_id = models.CharField(max_length=100,primary_key=True)
    first_name = models.CharField(max_length=25)
    last_name= models.CharField(max_length=25)
    company = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    phone_no1=  models.CharField(max_length=20)
    phone_no2= models.CharField(max_length=20)
    email = models.EmailField(max_length=50)
    subscription_date = models.DateField(null=True)
    website= models.URLField(max_length=100)

    def __str__(self):
        return self.customer_id 
    
