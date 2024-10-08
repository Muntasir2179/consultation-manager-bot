from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.forms import UserCreationForm
from .models import Customer, Users

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

        print(username, email, password, confirm_password)

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


def signout(request):
    # Clear all session data
    request.session.flush()
    return redirect('login')
