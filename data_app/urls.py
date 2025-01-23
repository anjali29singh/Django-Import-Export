
from django.urls import path ,include
from .views import ImportDataView,ProcessImportView

urlpatterns = [
     
    # path('upload/',uploadCsv,name='uploadCsv'),
    path('import/',ImportDataView.as_view(),name='importData'),
    path('process_import/',ProcessImportView.as_view(),name='process_import'),

]
