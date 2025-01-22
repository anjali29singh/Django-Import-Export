
from django.urls import path ,include
from .views import uploadCsv,ImportDataView,ExportDataView

urlpatterns = [
     
    path('upload/',uploadCsv,name='uploadCsv'),
    path('import/',ImportDataView.as_view(),name='importData'),
    path('export/',ExportDataView.as_view(),name='exportData'),

]
