from django.shortcuts import render, HttpResponse
from .models import Customer


# function to fetch all the data to the dashboard
def fetch_data(request):
    # fetching all the data from the database
    customers = Customer.objects.all().values('user_id',
                                              'person_name',
                                              'phone_number',
                                              'age',
                                              'appointment_date',
                                              'appointment_time',
                                              'appointment_end_time',
                                              'status')
    return render(request=request, template_name='index.html', context={'content': customers})


# function for chatbot
def chat(request):
    return render(request=request, template_name="chat.html")


# function for bot response
def get_response(request):
    user_message = request.GET.get('userMessage')
    return HttpResponse(user_message)


# function for signin
def login(request):
    return render(request=request, template_name='login.html')


# function for signup
def register(request):
    return render(request=request, template_name='register.html')

