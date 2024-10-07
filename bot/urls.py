from django.urls import path
from .views import bot, signup, signin


urlpatterns = [
    path("", view=bot, name='bot'),
    path("signin/", view=signin, name='signin'),
    path("signup/", view=signup, name='signup')
]
