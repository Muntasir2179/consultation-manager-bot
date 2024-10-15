from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from .models import Customer, Users
import json, os, yaml
from twilio.rest import Client


# for chatbot agent
from .tools import get_user_id
from .agent import DatabaseAgent
from .status_messages import data_update_message, status_approved_message, status_completed_message, status_rejected_message


database_agent = DatabaseAgent()

# creating twilio client
client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])


# loading the config file
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)


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
        context = {
            'content': customers,
            'username': request.session['username']
        }
        return render(request=request, template_name='index.html', context=context)
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


# function for sending response to whatsapp
@csrf_exempt
def get_response_for_whatsapp(request):
    sender_name = request.POST["ProfileName"]
    message_type = request.POST["MessageType"]
    whatsapp_id = request.POST["WaId"]
    message_status = request.POST["SmsStatus"]
    message_content = request.POST["Body"]
    receiver_number = request.POST["To"]
    sender_number = request.POST["From"]

    agent_response = database_agent.get_response(chat_session_id=sender_number, query=message_content)
    
    client.messages.create(from_=receiver_number,
                           body=agent_response,
                           to=sender_number)
    
    # checking if we do need to clear the chat history or not
    if agent_response.__contains__("request have been posted.") or agent_response.__contains__("successfully booked"): 
        # delete chat history when insertion is performed
        database_agent.clear_chat_history(chat_session_id=sender_number)
    elif agent_response.__contains__("Your appointment details have been updated."):
        # delete chat history when update is performed
        database_agent.clear_chat_history(chat_session_id=sender_number)
    elif agent_response.__contains__("Appointment canceled for user id"):
        # delete chat history when deletion is performed
        database_agent.clear_chat_history(chat_session_id=sender_number)

    return HttpResponse(content="Responding to whatsapp message.")


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


# function for sending feedback message
def send_feedback_message(previous_status:str, customer:Customer):
    message = """"""
    if previous_status == customer.status:
        message = data_update_message(customer)
    elif customer.status == "Approved":
        message = status_approved_message(customer)
    elif customer.status == "Completed":
        message = status_completed_message(customer)
    elif customer.status == "Rejected":
        message = status_rejected_message(customer)
    
    try:
        client.messages.create(from_=config['whatsapp-bot-number'],
                            body=message,
                            to=f"whatsapp:+88{customer.phone_number}")
        
        # store the recent feedback message into the chat history of that specific user
        database_agent.add_feedback_message_to_chat_history(chat_session_id=f"whatsapp:+88{customer.phone_number}",
                                                            feedback_message=message)
        return True
    except:
        return False


# function for editing data
def edit_customer(request, user_id:str):
    if "username" in request.session:
        if request.method == 'POST':
            customer = get_object_or_404(Customer, user_id=user_id)
            data = json.loads(request.body)
            
            previous_status = customer.status   # storing the previous status
            
            # Update the customer with new data
            customer.person_name = data.get('person_name')
            customer.phone_number = data.get('phone_number')
            customer.age = data.get('age')
            customer.appointment_date = data.get('appointment_date')
            customer.appointment_time = data.get('appointment_time')
            customer.appointment_end_time = data.get('appointment_end_time')
            customer.status = data.get('status')
            customer.save()

            # trying to send feedback message and getting operation status to check if it is done successfully or not
            operation_status = send_feedback_message(previous_status, customer)

            # delete the chat history when update is done
            if operation_status:
                database_agent.clear_chat_history(chat_session_id=f"whatsapp:+88{customer.phone_number}")

            return JsonResponse({'success': operation_status})
        return JsonResponse({'success': False})
    else:
        return redirect('login')


# function for delete data
def delete_customer(request, user_id:str):
    if "username" in request.session:
        if request.method == 'POST':
            customer = get_object_or_404(Customer, user_id=user_id)
            # delete the chat history of the user who's appointment is canceled
            database_agent.clear_chat_history(chat_session_id=f"whatsapp:+88{customer.phone_number}")
            customer.delete()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False})
    else:
        return redirect('login')


# function for adding customer appointment
@csrf_exempt
def add_customer(request):
    if request.method == 'POST':
        person_name = request.POST.get('add_person_name')
        phone_number = request.POST.get('add_phone_number')
        age = request.POST.get('add_age')
        appointment_date = request.POST.get('add_appointment_date')
        appointment_time = request.POST.get('add_appointment_time')
        appointment_end_time = request.POST.get('add_appointment_end_time')
        status = request.POST.get('add_status')

        print(appointment_time)

        # Create a new customer
        customer = Customer.objects.create(
            user_id=get_user_id(phone_number=phone_number, sc_date=appointment_date, sc_time=appointment_time),
            person_name=person_name,
            phone_number=phone_number,
            age=age,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            appointment_end_time=appointment_end_time,
            status=status
        )

        # Return success response with customer data
        return JsonResponse({
            'success': True,
            'customer': {
                'user_id': customer.user_id,  # assuming user_id is auto-generated
                'person_name': customer.person_name,
                'phone_number': customer.phone_number,
                'age': customer.age,
                'appointment_date': customer.appointment_date,
                'appointment_time': customer.appointment_time,
                'appointment_end_time': customer.appointment_end_time,
                'status': customer.status
            }
        })
    
    return JsonResponse({'success': False})


# function for handling bad request
def custom_404_view(request, exception=None):
    return render(request, '404.html', {}, status=404)

