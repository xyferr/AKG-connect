from django.urls import path,include
from . import  views

urlpatterns = [
    path("", views.Get_attendance, name="attendance"),
    path("pdp", views.get_pdp_attendance, name="pdp"),
]
