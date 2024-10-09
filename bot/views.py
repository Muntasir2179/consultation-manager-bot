from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from .models import Customer, Users
import json

# for chatbot agent
from .agent import DatabaseAgent


database_agent = DatabaseAgent()

# function to fetch all the data to the dashboard
def fetch_data(request):
    # fetching all the data from the database
    if 'username' in request.session:
        customers = Customer.objects.all().values('user_id',
                                                'person_name',
                                                'phone_number',
                                                'age',
                                                'appointment_date',
                                                'appointment_time',
                                                'appointment_end_time',
                                                'status')
        return render(request=request, template_name='index.html', context={'content': customers})
    else:
        return redirect('login')


# function for chatbot
def chat(request):
    return render(request=request, template_name="chat.html")


# function for bot response
def get_response(request):
    user_message = request.GET.get('userMessage')
    agent_response = database_agent.get_response(query=user_message)
    return HttpResponse(agent_response)


# function for signin
def login(request):
    if request.method == "GET":
        return render(request=request, template_name='login.html')
    if request.method == "POST":
        input_username = request.POST.get('username')
        input_password = request.POST.get('password')

        try:
            user = Users.objects.get(username=input_username)
            if user.password == input_password:
                request.session['username'] = input_username    # store the username in the session
                print(input_username, input_password)
                return redirect("fetch_data")
        except:
            return render(request=request, template_name='login.html')


# function for signup
def register(request):
    if request.method == 'GET':
        form = UserCreationForm()
        context = {
            "form": form
        }
        return render(request, 'register.html', context=context)

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            try:
                new_user = Users(
                    username=username,
                    email=email,
                    password=password,
                    confirm_password=confirm_password
                )
                new_user.save()
                return redirect('login')
            except:
                return render(request=request, template_name="register.html")


# function for signout
def signout(request):
    # Clear all session data
    request.session.flush()
    return redirect('login')


# function for editing data
def edit_customer(request, user_id: int):
    if "username" in request.session:
        if request.method == 'POST':
            customer = get_object_or_404(Customer, user_id=user_id)
            data = json.loads(request.body)

            # Update the customer with new data
            customer.person_name = data.get('person_name')
            customer.phone_number = data.get('phone_number')
            customer.age = data.get('age')
            customer.appointment_date = data.get('appointment_date')
            customer.appointment_time = data.get('appointment_time')
            customer.appointment_end_time = data.get('appointment_end_time')
            customer.status = data.get('status')
            customer.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False})
    else:
        return redirect('login')


# function for delete data
def delete_customer(request, user_id: int):
    if "username" in request.session:
        if request.method == 'POST':
            customer = get_object_or_404(Customer, user_id=user_id)
            customer.delete()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False})
    else:
        return redirect('login')
