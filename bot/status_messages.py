from .models import Customer



def data_update_message(customer: Customer):
    return f"""
    Your data has been updated. Your user id is {customer.user_id}.

    Name: {customer.person_name}
    Phone: {customer.phone_number}
    Age: {customer.age}
    
    Appointment Schedule:
        Date: {customer.appointment_date}
        Time: {customer.appointment_time} - {customer.appointment_end_time}
    
    Status: {customer.status}

    See you on due time.
    """


def status_approved_message(customer: Customer):
    return f"""
    Your request for appointment has been approved. Your user id is {customer.user_id}.

    Name: {customer.person_name}
    Phone: {customer.phone_number}
    Age: {customer.age}
    
    Appointment Schedule:
        Date: {customer.appointment_date}
        Time: {customer.appointment_time} - {customer.appointment_end_time}
    
    Status: {customer.status}

    See you on due time.
    """


def status_completed_message(customer: Customer):
    return f"""
    Your appointment has been completed. Your user id was {customer.user_id}.

    Name: {customer.person_name}
    Phone: {customer.phone_number}
    Age: {customer.age}
    
    Appointment Schedule:
        Date: {customer.appointment_date}
        Time: {customer.appointment_time} - {customer.appointment_end_time}
    
    Status: {customer.status}

    Have a nice day.
    """


def status_rejected_message(customer: Customer):
    return f"""
    Your request for appointment has been rejected. Your user id is {customer.user_id}.

    Name: {customer.person_name}
    Phone: {customer.phone_number}
    Age: {customer.age}
    
    Appointment Schedule:
        Date: {customer.appointment_date}
        Time: {customer.appointment_time} - {customer.appointment_end_time}
    
    Status: {customer.status}

    Please contact with the support team to get the issue resolved.
    """
