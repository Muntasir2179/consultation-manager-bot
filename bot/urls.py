from django.urls import path
from .views import fetch_data, register, login, chat, get_response


urlpatterns = [
    path("", view=fetch_data, name='fetch_data'),
    path("login/", view=login, name='login'),
    path("register/", view=register, name='register'),
    path("chat/", view=chat, name='chat'),
    path("get-response/", view=get_response, name='get_response')
]
