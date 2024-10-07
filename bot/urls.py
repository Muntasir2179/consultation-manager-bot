from django.urls import path
from .views import fetch_data, register, login


urlpatterns = [
    path("", view=fetch_data, name='fetch_data'),
    path("login/", view=login, name='login'),
    path("register/", view=register, name='register')
]
