from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework.response import Response
import pandas as pd
from rest_framework.permissions import IsAuthenticated 
from .models import CustomerModel
from rest_framework.views import APIView
from .resources import CustomerResource
from tablib import Dataset
from rest_framework.parsers import MultiPartParser
import io
from django.views import View
from import_export.admin import ImportMixin
from django.urls import path, reverse, reverse_lazy
from django.forms import forms
from import_export.signals import post_import

class MyCustomMixin(ImportMixin):

    resource_class = CustomerResource
    model = CustomerModel
    media = forms.Media()





class ImportDataView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]
    


    def get(self,request):


        mixin = MyCustomMixin()
        mixin.import_action(request)
        
        return Response("get request called")


    def post(self, request):
        mixin = MyCustomMixin().import_action(request)

        # print(mixin)

        return render(request, mixin)
        file = request.FILES['file']
        if not file:
            return Response({'error': 'Please upload a CSV file'}, status=400)
                
        if not file.name.endswith('.csv'):
            return Response({'error': 'File must be CSV format'}, status=400)
            




        # dataset = Dataset()
        # text_file = io.TextIOWrapper(file,encoding='utf-8')
        # imported_data = dataset.load(text_file.read(), format='csv')
        # customer_resource = CustomerResource(model=CustomerModel) 

        # mixin import


        

         
        # result = customer_resource.import_data(dataset, dry_run=True,raise_errors=True)
        
        # if result.has_errors():

        #     print("result has error",result)
        #     return Response({
        #         'error': 'Invalid CSV format or data',
        #         'errors': [
        #                 {
        #                     'row': err.row_number,
        #                     'errors': [str(e) for e in err.errors]
        #                 } 
        #                 for err in result.row_errors()
        #             ]
        #         }, status=400)
                
        # result = customer_resource.import_data(dataset, dry_run=False)
        # return Response({
        #         'success': True,
        #         'message': f'Successfully imported {result.total_rows} rows'
        #     })
            
    # def get(self, request):
    #     return render(request, 'upload_file.html')









class ProcessImportView(APIView):

    pass














