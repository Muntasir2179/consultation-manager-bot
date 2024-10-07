import os
from dotenv import load_dotenv
from twilio.rest import Client
from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt


# loading the environment variables
# load_dotenv()


# client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])

# # Create your views here.
# @csrf_exempt
# def bot(request):
#     sender_name = request.POST["ProfileName"]
#     message_type = request.POST["MessageType"]
#     whatsapp_id = request.POST["WaId"]
#     message_status = request.POST["SmsStatus"]
#     message_content = request.POST["Body"]
#     receiver_number = request.POST["To"]
#     sender_number = request.POST["From"]
    
#     client.messages.create(from_=receiver_number,
#                            body=f"Hi {sender_name}, how's it going",
#                            to=sender_number)
    
#     return HttpResponse(content="Hi I am Muntasir")


def bot(request):
    return render(request=request, template_name='index.html')