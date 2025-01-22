from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
import pandas as pd
from rest_framework.permissions import IsAuthenticated 
from .models import CustomerModel
from rest_framework.views import APIView
from .resources import CustomerResource
from tablib import Dataset
from rest_framework.parsers import MultiPartParser
import io

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



# sir code 

class ExportDataView(APIView):
    permission_classes= [IsAuthenticated]

    def get(self,request):
        resource = CustomerResource()
        dataset= resource.export()
        response = HttpResponse(dataset.csv,content_type='text/csv') 
        response['Content-Disposition'] = 'attachment; filename="exported_data.csv"'

        return response



class ImportDataView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]
    
    def post(self, request):
        file = request.FILES['file']
        if not file:
            return Response({'error': 'Please upload a CSV file'}, status=400)
                
        if not file.name.endswith('.csv'):
            return Response({'error': 'File must be CSV format'}, status=400)
            

        customer_resource = CustomerResource(model=CustomerModel) 
        dataset = Dataset()
        text_file = io.TextIOWrapper(file,encoding='utf-8')
        imported_data = dataset.load(text_file.read(), format='csv')
            
        print("imported_data",imported_data.dict[:3])
        result = customer_resource.import_data(dataset, dry_run=True)
        
        if result.has_errors():

            print("result has error",result)
            return Response({
                'error': 'Invalid CSV format or data',
                'errors': [
                        {
                            'row': err.row_number,
                            'errors': [str(e) for e in err.errors]
                        } 
                        for err in result.row_errors()
                    ]
                }, status=400)
                
        result = customer_resource.import_data(dataset, dry_run=False)
        return Response({
                'success': True,
                'message': f'Successfully imported {result.total_rows} rows'
            })
            
    def get(self, request):
        return render(request, 'upload_file.html')