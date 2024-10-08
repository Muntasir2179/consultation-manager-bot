from django.contrib import admin
from .models import Customer, Users

# Register your models here.
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("user_id", "person_name", "phone_number", "status")
    list_display_links = ("user_id", "person_name", "phone_number")

class UsersAdmin(admin.ModelAdmin):
    list_display = ("username", "email")
    list_display_links = ("username", "email")


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Users, UsersAdmin)
