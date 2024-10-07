from django.contrib import admin
from .models import Customer

# Register your models here.
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user_id', "person_name", "phone_number", "status")
    list_display_links = ('user_id', "person_name", "phone_number")

admin.site.register(Customer, CustomerAdmin)
