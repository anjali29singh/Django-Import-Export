
from django.urls import path ,include
from .views import uploadCsv

urlpatterns = [
     
    path('upload/',uploadCsv,name='uploadCsv')
]
