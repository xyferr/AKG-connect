from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('fetch_user_details/<str:user_id>/<str:auth_token>/', views.fetch_user_details, name='fetch_user_details'),
]
