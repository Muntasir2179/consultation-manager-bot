from django.urls import path
from django.conf.urls import handler404
from .views import fetch_data, register, login, chat, get_response, signout, delete_customer, edit_customer, add_customer


handler404 = 'bot.views.custom_404_view'

urlpatterns = [
    path("", view=fetch_data, name='fetch_data'),
    path("login/", view=login, name='login'),
    path("register/", view=register, name='register'),
    path("chat/", view=chat, name='chat'),
    path("get-response/", view=get_response, name='get_response'),
    path('signout/', view=signout, name="signout"),
    path('delete-customer/<int:user_id>/', view=delete_customer, name="delete_customer"),
    path('edit-customer/<int:user_id>/', view=edit_customer, name='edit_customer'),
    path('add-customer/', view=add_customer, name='add_customer'),
]
