from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated 
from .models import CustomerModel
from rest_framework.views import APIView
from .resources import CustomerResource
from rest_framework.parsers import MultiPartParser
import io
from django.views import View
from import_export.admin import ImportMixin
from django.contrib.admin.views.main import ChangeList
from django.forms import forms

class MyCustomMixin(ImportMixin):

    resource_class = CustomerResource
    model = CustomerModel
    media = forms.Media()

    
    def handle_import_actions(self,request):
        if not hasattr(self,"import_action"):
            return HttpResponseBadRequest("No import action defined")

        return self.import_action(request)

    def handle_process_import(self,request):
        if not hasattr(self,"process_import"):
            return HttpResponseBadRequest("import action not implemented")

        return self.process_import(request)
    
    

class ImportDataView(APIView,MyCustomMixin):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]
    

    def get(self,request):
    


        response= self.handle_import_actions(request)
        
        return Response("get request called")


    def post(self, request):

        response = self.handle_import_actions(request)
        return JsonResponse({"response":response})
    
class ProcessImportView(APIView,MyCustomMixin):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]
    def post(self,request):

        response =  self.handle_process_import(request)

        return Response("process import view called")











