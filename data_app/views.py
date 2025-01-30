from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated 
from .models import CustomerModel
from rest_framework.views import APIView
from .resources import CustomerResource,CustomerAdminResources
from rest_framework.parsers import MultiPartParser
import io
from django.views import View
from import_export.admin import ImportMixin
from django.contrib.admin.views.main import ChangeList
from django.forms import forms
from .admin import MyCustomerAdmin
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from bs4 import BeautifulSoup
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.conf import settings
from import_export.forms import ImportExportFormBase
import warnings
from django.utils.decorators import method_decorator


class MyCustomMixin(ImportMixin):

    media = forms.Media()
    admin = MyCustomerAdmin(CustomerModel,CustomerAdminResources)


    def get_html_value(self,diff):
        soup = BeautifulSoup(diff, 'html.parser')
        if soup.span:
            return soup.span.contents[0]
        elif soup.find('ins'):
            return soup.find('ins').text

    def create_response_structure(self,context,import_form):

        result = context.get('result').__dict__

        diff_headers =result["diff_headers"]
        

        response_data={


            "import_payload":{

                "import_file_name":import_form.cleaned_data['import_file'].tmp_storage_name,
                    "original_file_name":import_form.cleaned_data['import_file'].name,
                    "input_format":import_form.cleaned_data['input_format'],
                    "resource":import_form.cleaned_data.get("resource",""),
                    "confirm":"Confirm import"
            },
        }


        import_data=[]

        # print(result.rows[0].__dict__.get('diff'))

        for row in result['rows']:
            
            row_dict= row.__dict__
            
            
            temp={}


            errors_row=[]  # list of error in each row of csv
            for error in row_dict.get('errors'):
                errors_row.append(str(error.__dict__['error']))
            
            temp['errors']=errors_row

            if row_dict.get('validation_error'):
                validation_errors=[] #  dict of validation error
                for key in row_dict.get('validation_error'):
                    
                    valid_error_row= {}
                    valid_error_row[key]=row_dict['validation_error'][key]

                    validation_errors.append(valid_error_row)
                temp['validation_errors']=validation_errors

            else:
                temp['validation_errors']=row_dict['validation_error']
            temp['new_record']=row_dict['new_record']
            temp['import_type']=row_dict['import_type']
            temp['row_values']=row_dict['row_values']
            field_values={}

            diff =row_dict['diff'] 
            if diff:
            
                for i in range (len(diff_headers)):

                    value = self.get_html_value(diff[i])
                    field_values[diff_headers[i]]=value
            
            temp['row']=field_values
            
            import_data.append(temp)
            
        response_data['import_data']=import_data

        print("import data is",import_data)

        return JsonResponse(response_data)

        

    def import_action(self, request, *args, **kwargs):
        """
        Perform a dry_run of the import to make sure the import will not
        result in errors.  If there are no errors, save the user
        uploaded file to a local temp file that will be used by
        'process_import' for the actual import.
        """

        if not self.has_import_permission(request):
            raise PermissionDenied

        context = self.get_import_context_data()

        import_formats = self.get_import_formats()
        if getattr(self.get_form_kwargs, "is_original", False):
            # Use new API
            import_form = self.create_import_form(request)
        else:
            form_class = self.get_import_form_class(request)
            form_kwargs = self.get_form_kwargs(form_class, *args, **kwargs)

            if issubclass(form_class, ImportExportFormBase):
                import_form = form_class(
                    import_formats,
                    self.get_import_resource_classes(),
                    request.POST or None,
                    request.FILES or None,
                    **form_kwargs
                )
            else:
                warnings.warn(
                    "The ImportForm class must inherit from ImportExportFormBase, "
                    "this is needed for multiple resource classes to work properly. ",
                    category=DeprecationWarning
                )
                import_form = form_class(
                    import_formats,
                    request.POST or None,
                    request.FILES or None,
                    **form_kwargs
                )

        resources = list()
        if request.POST and import_form.is_valid():
            
            input_format = import_formats[int(import_form.cleaned_data['input_format'])]()
            if not input_format.is_binary():
                input_format.encoding = self.from_encoding
            import_file = import_form.cleaned_data['import_file']

            if getattr(settings, "IMPORT_EXPORT_SKIP_ADMIN_CONFIRM", False):
                # This setting means we are going to skip the import confirmation step.
                # Go ahead and process the file for import in a transaction
                # If there are any errors, we roll back the transaction.
                # rollback_on_validation_errors is set to True so that we rollback on
                # validation errors. If this is not done validation errors would be
                # silently skipped.
                data = bytes()
                for chunk in import_file.chunks():
                    data += chunk
                try:
                    dataset = input_format.create_dataset(data)
                except Exception as e:
                    self.add_data_read_fail_error_to_form(import_form, e)
                if not import_form.errors:
                    result = self.process_dataset(dataset, import_form, request, *args, raise_errors=False,
                                                  rollback_on_validation_errors=True, **kwargs)

                    if not result.has_errors() and not result.has_validation_errors():
                        return self.process_result(result, request)
                    else:
                        context['result'] = result
            else:
                # first always write the uploaded file to disk as it may be a
                # memory file or else based on settings upload handlers
                tmp_storage = self.write_to_tmp_storage(import_file, input_format)
                # allows get_confirm_form_initial() to include both the
                # original and saved file names from form.cleaned_data
                import_file.tmp_storage_name = tmp_storage.name

                try:
                    # then read the file, using the proper format-specific mode
                    # warning, big files may exceed memory
                    data = tmp_storage.read()
                    dataset = input_format.create_dataset(data)
                    
                except Exception as e:
                    self.add_data_read_fail_error_to_form(import_form, e)

                if not import_form.errors:
                    # prepare kwargs for import data, if needed
                    res_kwargs = self.get_import_resource_kwargs(request, form=import_form, *args, **kwargs)
                    resource = self.choose_import_resource_class(import_form)(**res_kwargs)
                    resources = [resource]
                    
                    # prepare additional kwargs for import_data, if needed
                    imp_kwargs = self.get_import_data_kwargs(request, form=import_form, *args, **kwargs)
                    result = resource.import_data(dataset, dry_run=True,
                                                  raise_errors=False,
                                                  file_name=import_file.name,
                                                  user=request.user,
                                                  **imp_kwargs)
                    
                    

                    context['result'] = result

                    #  create 
                

                    if not result.has_errors() and not result.has_validation_errors():
                        
                        if getattr(self.get_form_kwargs, "is_original", False):
                            # Use new API
                            context["confirm_form"] = self.create_confirm_form(
                                request, import_form=import_form
                            )
                        else:
                            confirm_form_class = self.get_confirm_form_class(request)
                            initial = self.get_confirm_form_initial(request, import_form)
                            context["confirm_form"] = confirm_form_class(
                                initial=self.get_form_kwargs(form=import_form, **initial)
                            )





        else:
            res_kwargs = self.get_import_resource_kwargs(request, form=import_form, *args, **kwargs)
            resource_classes = self.get_import_resource_classes()
            resources = [resource_class(**res_kwargs) for resource_class in resource_classes]

        # context.update(self.admin_site.each_context(request))
        
        context['title'] = _("Import")
        context['form'] = import_form
        context['opts'] = self.model._meta
        context['media'] = self.media + import_form.media
        context['fields_list'] = [
            (resource.get_display_name(), [f.column_name for f in resource.get_user_visible_fields()])
            for resource in resources
        ]

        request.current_app = "data app"
        

        if request.POST:

            result = context.get('result').__dict__
            if request.path.startswith('/admin/'):
                print("admifn")
                return TemplateResponse(request, [self.import_template_name],context)
            return self.create_response_structure(context,import_form)
               

             

        
        return TemplateResponse(request, [self.import_template_name],
                                context)
    

    

    @method_decorator(require_POST)
    def process_import(self, request, *args, **kwargs):
        """
        Perform the actual import action (after the user has confirmed the import)
        """
        if not self.has_import_permission(request):
            raise PermissionDenied
        
        if getattr(self.get_confirm_import_form, 'is_original', False):
            confirm_form = self.create_confirm_form(request)
        
        else:
            form_type = self.get_confirm_import_form()
            confirm_form = form_type(request.POST)
        print("confimr form is",confirm_form)

        if confirm_form.is_valid():
            import_formats = self.get_import_formats()
            input_format = import_formats[
                int(confirm_form.cleaned_data['input_format'])
            ](encoding=self.from_encoding)
            encoding = None if input_format.is_binary() else self.from_encoding
            tmp_storage_cls = self.get_tmp_storage_class()
            tmp_storage = tmp_storage_cls(
                name=confirm_form.cleaned_data['import_file_name'],
                encoding=encoding,
                read_mode=input_format.get_read_mode()
            )

            data = tmp_storage.read()
            dataset = input_format.create_dataset(data)
            result = self.process_dataset(dataset, confirm_form, request, *args, **kwargs)

            tmp_storage.remove()
            print("rqeust is",request.__dict__)
            return self.process_result(result, request)
    def handle_import_actions(self,request):
        if not hasattr(self,"import_action"):
            return HttpResponseBadRequest("No import action defined")

        return self.admin.import_action(request)


    def handle_process_import(self,request):
        if not hasattr(self,"process_import"):
            return HttpResponseBadRequest("import action not implemented")
        
        return self.admin.process_import(request)
    
    

class ImportDataView(APIView,MyCustomMixin):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]
    

    def get(self,request):
    
        response= self.handle_import_actions(request)
        
        return Response("get request called")


    def post(self, request):

        response = self.handle_import_actions(request)

        
        return HttpResponse(response)
    
class ProcessImportView(APIView,MyCustomMixin):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]
    def post(self,request):

        response =  self.handle_process_import(request)

        return Response("process import view called")











