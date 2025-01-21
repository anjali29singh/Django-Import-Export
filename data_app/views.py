from rest_framework.decorators import api_view
from rest_framework.response import Response
import pandas as pd
from .models import CustomerModel
from django.shortcuts import render,redirect
from django.contrib import messages

@api_view(['GET','POST'])
def uploadCsv(request):
    if request.method == 'POST' and request.FILES['file']:
        csv_file = request.FILES['file']

        # Check if the uploaded file is a CSV
        if not csv_file.name.endswith('.csv'):
            messages.error(request, "The file must be a CSV.")
            return redirect('uploadCsv')

        try:
            # Read the CSV file into a pandas DataFrame
            df = pd.read_csv(csv_file)

            # Loop through the rows of the CSV file and insert them into the database
            for _, row in df.iterrows():
                customer, created = CustomerModel.objects.get_or_create(
                    index=row['Index'],
                    customer_id=row['Customer Id'],
                    first_name=row['First Name'],
                    last_name=row['Last Name'],
                    company=row['Company'],
                    city=row['City'],
                    country=row['Country'],
                    phone_no1=row['Phone 1'],
                    phone_no2=row['Phone 2'],
                    email=row['Email'],
                    subscription_date=row['Subscription Date'],
                    website=row['Website']
                )
                
                if created:
                    messages.success(request, f"Created new customer: {customer.first_name} {customer.last_name}")
                else:
                    messages.warning(request, f"Customer already exists: {customer.first_name} {customer.last_name}")

            messages.success(request, "File uploaded and processed successfully.")
            return redirect('uploadCsv')
        
        except Exception as e:
            messages.error(request, f"Error processing the CSV file: {str(e)}")
            return redirect('uploadCsv')

    # Render the page with the form when method is GET
    return render(request, 'upload_file.html')