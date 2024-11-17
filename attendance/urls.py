from django.urls import path,include
from . import  views

urlpatterns = [
    path("", views.Get_attendance, name="attendance"),
]
