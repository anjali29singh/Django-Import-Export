
from django.urls import path ,include
from .views import ImportDataView,ProcessImportView

app_label="data_app"
urlpatterns = [
     
    path('import/',ImportDataView.as_view(),name='importData'),
    path('process_import/',ProcessImportView.as_view(),name='process_import'),

]
