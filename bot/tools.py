# for config and env variables
import yaml
from dotenv import load_dotenv

# for database
import mysql.connector
from datetime import timedelta, datetime

# for custom tool define
import re
from typing import Optional, ClassVar, Union
from pydantic import BaseModel, Field, field_validator
from langchain.tools import tool

# for error analyzer and response rephraser llm
from langchain_groq import ChatGroq
from .prompt import error_prompt, result_rephraser_prompt
from langchain_core.output_parsers import StrOutputParser


# loading the config file and environment variables
load_dotenv()
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)


# building chains
class Chains:
    llm = ChatGroq(model=config["error-model-name"])
    error_generator_chain = error_prompt | llm | StrOutputParser()    # creating error generator chain
    result_rephraser_chain = result_rephraser_prompt | llm | StrOutputParser()    # result rephraser chain


# establishing connection to the mysql server
def get_connection():
    conn = mysql.connector.connect(host=config["database"]["host"],
                                   user=config["database"]["user"],
                                   password=config["database"]["password"],
                                   database=config["database"]["database"])
    return conn, conn.cursor()


# class of validators functions
class BaseSchema(BaseModel):
    valid_prefixes: ClassVar[list] = ["013", "017", "018", "019", "015", "016"]

    @classmethod
    def validate_user_id(cls, value):
        if isinstance(value, str):
            if len(value) == 23:
                first, ph, d, t, s = value.split("_")
                if first == 'SC' and len(ph) == 11 and len(d+t+s) == 6:
                    return value
        return "Invalid user id."

    @classmethod
    def validate_phone_number(cls, value:str):
        has_error = False
        error_message = 'Invalid phone number. '
        # Check if the phone number has exactly 11 digits
        if not re.fullmatch(r'\d{11}', value):
            error_message = error_message + 'It must have exactly 11 digits.'
            has_error = True

        # Check if the phone number starts with a valid prefix
        if not any(value.startswith(prefix) for prefix in cls.valid_prefixes):
            error_message = error_message + f' It must start with one of the following prefixes: {cls.valid_prefixes}.'
            has_error = True
        return Chains.error_generator_chain.invoke(input={"input": error_message}) if has_error else value
    
    @classmethod
    def validate_appointment_date(cls, value:str):
        try:
            datetime.strptime(value, '%Y-%m-%d')
        except Exception as e:
            return 'Invalid date. It must be in the format YYYY-MM-DD'
        return value

    @classmethod
    def validate_appointment_time(cls, value:str):
        try:
            formatted_time = datetime.strptime(value, "%H:%M:%S")
            formatted_time = formatted_time.strftime("%I:%M:%S")  # 12-hour format with AM/PM
            return formatted_time
        except:
            try:
                formatted_time = datetime.strptime(value, "%H:%M")
                formatted_time = formatted_time.strftime("%I:%M:%S")  # 12-hour format with AM/PM
                return formatted_time
            except:
                return 'Invalid time. It must be in H:M:S and 12 hour format.'
    
    @classmethod
    def validate_age(cls, value):
        if isinstance(value, int):
            if value >= 20 and value <= 100:
                return value
        return "Invalid age. It should be between 20-100."


# schema for insert_data tool
class DatabaseInsertSchema(BaseSchema):
    phone_number: str = Field(description="Should be a valid phone number of 11 digits and it can only starts with 013, 017, 018, 019, 015, 016")
    person_name: str = Field(description="It should be a valid name")
    appointment_date: str = Field(description="It should be a date with the format YY-MM-DD")
    appointment_time: str = Field(description="It will be a time with the format H:M:S")
    age: Optional[Union[int, str]] = Field(description="It will be an integer within the range of 20-100", default=None)
    
    @field_validator('phone_number')
    def phone_number_validate(cls, value:str):
        return cls.validate_phone_number(value)
    
    @field_validator('appointment_date')
    def appointment_date_validate(cls, value:str):
        return cls.validate_appointment_date(value)
    
    @field_validator('appointment_time')
    def appointment_time_validate(cls, value:str):
        return cls.validate_appointment_time(value)
    
    @field_validator('age')
    def age_validate(cls, value):
        return cls.validate_age(value)


# schema for update_data tool
class DatabaseUpdateSchema(BaseSchema):
    user_id: Union[int, str] = Field(description="It should be a valid integer number greater than zero.")
    phone_number: Optional[str] = Field(description="Should be a valid phone number of 11 digits and it can only starts with 013, 017, 018, 019, 015, 016", default=None)
    person_name: Optional[str] = Field(description="It should be a valid name", default=None)
    appointment_date: Optional[str] = Field(description="It should be a date with the format YY-MM-DD", default=None)
    appointment_time: Optional[str] = Field(description="It will be a time with the format H:M:S", default=None)
    age: Optional[Union[int, str]] = Field(description="It will be an integer within the range of 20-100", default=None)

    @field_validator('user_id')
    def user_id_validate(cls, value):
        return cls.validate_user_id(value)

    @field_validator('phone_number')
    def phone_number_validate(cls, value:str):
        return cls.validate_phone_number(value)
    
    @field_validator('appointment_date')
    def appointment_date_validate(cls, value:str):
        return cls.validate_appointment_date(value)
    
    @field_validator('appointment_time')
    def appointment_time_validate(cls, value:str):
        return cls.validate_appointment_time(value)
    
    @field_validator('age')
    def age_validate(cls, value):
        return cls.validate_age(value)


# schema for search_data tool
class DatabaseSearchSchema(BaseSchema):
    user_id: Union[int, str] = Field(description="It should be a valid integer number greater than zero.")

    @field_validator('user_id')
    def user_id_validate(cls, value):
        return cls.validate_user_id(value)


# schema for delete_data tool
class DatabaseDeleteSchema(BaseSchema):
    user_id: Union[int, str] = Field(description="It should be a valid integer number greater than zero.")

    @field_validator('user_id')
    def user_id_validate(cls, value):
        return cls.validate_user_id(value)


# function for formatting search result
def format_search_result(result):
    if result is None:
        return None
    _, user_id, phone_number, person_name, age, appointment_date, appointment_time, appointment_end_time, status = result
    formatted_date = appointment_date.strftime("%d-%m-%Y")
    formatted_appointment_time = str(timedelta(seconds=appointment_time.seconds))[:-3]
    formatted_appointment_end_time = str(timedelta(seconds=appointment_end_time.seconds))[:-3]
    response = (f"\nUser id              : {user_id}\n"
                f"Person name          : {person_name}\n"
                f"Phone number         : {phone_number}\n"
                f"Age                  : {age}\n"
                f"Appointment date     : {formatted_date}\n"
                f"Appointment time     : {formatted_appointment_time}\n"
                f"Appointment end time : {formatted_appointment_end_time}\n"
                f"Status               : {status}")
    return Chains.result_rephraser_chain.invoke(input={"input": response})


# defining custom insert_data tool
@tool("insert_data", args_schema=DatabaseInsertSchema, return_direct=True)
def insert_data(phone_number: str, person_name: str, appointment_date: str, appointment_time: str, age: int = None, status : str = "Pending"):
    """This function inserts data into database table. Use this function only when you need to insert some data into the database."""

    # calculating appointment end time
    try:
        appointment_time_obj = datetime.strptime(appointment_time, "%H:%M:%S")
        appointment_end_time_obj = appointment_time_obj + timedelta(minutes=5)
        appointment_end_time = appointment_end_time_obj.strftime("%H:%M:%S")
    except Exception as e:
        return Chains.error_generator_chain.invoke(input={"input": f"{e}"})

    user_id = get_user_id(phone_number=phone_number, sc_date=appointment_date, sc_time=appointment_time)
    
    try:
        conn, cursor = get_connection()
        # SQL query to search and insert data into the table
        insert_query = f'''
        INSERT INTO {config["database"]["table"]} (user_id, phone_number, person_name, age, appointment_date, appointment_time, appointment_end_time, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        '''
        search_query = f'''
        SELECT * FROM {config["database"]["table"]} WHERE user_id = %s
        AND person_name = %s
        AND phone_number = %s
        AND age = %s
        AND appointment_date = %s
        AND appointment_time = %s
        AND appointment_end_time = %s
        '''
        # check if the data already exists in the database or not
        cursor.execute(search_query, (user_id, person_name, phone_number, age, appointment_date, appointment_time, appointment_end_time))
        search_result = cursor.fetchone()

        if search_result is None:
            cursor.execute(insert_query, (user_id, phone_number, person_name, age, appointment_date, appointment_time, appointment_end_time, status))
            conn.commit()
            current_user_id = user_id
        else:
            current_user_id = search_result[1]

        if conn.is_connected():
            cursor.close()
            conn.close()
        return f"Your appointment request have been posted. Your ID number is {current_user_id}."
    except Exception as e:
        return Chains.error_generator_chain.invoke(input={"input": f"{e}"})


# defining custom search_data tool
@tool("search_data", args_schema=DatabaseSearchSchema, return_direct=True)
def search_data(user_id: str):
    """This function takes a phone number and searches record in database. Use this function only when you need to search some data into the database."""
    conn, cursor = get_connection()
    result = None
    try:
        search_query = f"SELECT * FROM {config["database"]["table"]} WHERE user_id = %s"   # sql query for searching data
        cursor.execute(search_query, (user_id,))
        result = format_search_result(cursor.fetchone())
        if conn.is_connected():
            cursor.close()
            conn.close()
        
        if user_id.__contains__("Invalid"):
            return user_id    # it would be an error message
        return result if result is not None else f"No appointment booked with user id {user_id}."
    except Exception as e:
        return Chains.error_generator_chain.invoke(input={"input": f"{e}"})


# defining custom update_data tool
@tool("update_data", args_schema=DatabaseUpdateSchema, return_direct=True)
def update_data(user_id,
                phone_number: str = None,
                person_name: str = None,
                age: int = None,
                appointment_date: str = None,
                appointment_time: str = None):
    """This function takes several data in order to update the database. Use this tool when you need to update some information in database table."""
    try:
        # establishing connection to the database
        conn, cursor = get_connection()
        
        # Check if the phone number exists
        search_query = f"SELECT * FROM {config["database"]["table"]} WHERE user_id = %s"    # sql query for searching data
        cursor.execute(search_query, (user_id,))
        result = cursor.fetchone()
        
        if result:  # when there is a data exist to update
            update_fields = []
            update_values = []

            if phone_number:
                update_fields.append("phone_number = %s")
                update_values.append(phone_number)
            
            if person_name:
                update_fields.append("person_name = %s")
                update_values.append(person_name)
            
            if age is not None:
                update_fields.append("age = %s")
                update_values.append(age)
            
            if appointment_date:
                # Check if the date is in 'day-month-year' format and convert it if needed
                try:
                    # Try to convert from 'DD-MM-YYYY' format to 'YYYY-MM-DD' format
                    appointment_date_obj = datetime.strptime(appointment_date, "%d-%m-%Y")
                    formatted_appointment_date = appointment_date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    # If it's already in 'YYYY-MM-DD', use it directly
                    formatted_appointment_date = appointment_date

                update_fields.append("appointment_date = %s")
                update_values.append(formatted_appointment_date)
            
            if appointment_time:
                # Handle both 'HH:MM' and 'HH:MM:SS' formats by slicing to 'HH:MM'
                try:
                    appointment_time_obj = datetime.strptime(appointment_time[:5], "%H:%M")
                except Exception as e:
                    return Chains.error_generator_chain.invoke(input={"input": f"{e}"})

                # Appointment end time is 5 minutes later
                appointment_end_time_obj = appointment_time_obj + timedelta(minutes=5)
                formatted_appointment_time = appointment_time_obj.strftime("%H:%M:%S")
                formatted_appointment_end_time = appointment_end_time_obj.strftime("%H:%M:%S")
                
                update_fields.append("appointment_time = %s")
                update_values.append(formatted_appointment_time)
                
                update_fields.append("appointment_end_time = %s")
                update_values.append(formatted_appointment_end_time)
            
            # Only update if there are fields to update
            if update_fields:
                update_query = f"UPDATE {config["database"]["table"]} SET {', '.join(update_fields)} WHERE user_id = %s"
                update_values.append(user_id)  # Add the phone_number to the end for the WHERE clause
                cursor.execute(update_query, tuple(update_values))
                conn.commit()

                # fetch the updated result
                cursor.execute(search_query, (user_id,))
                updated_result = cursor.fetchone()

                if conn.is_connected():
                    cursor.close()
                    conn.close()
                
                return ("Your appointment details have been updated.\n"
                        f"{format_search_result(updated_result)}")
            else:
                return "No new information provided to update."
        else:
            if user_id.__contains__("Invalid"):
                return user_id    # it will be an error message rather than user id
            return f"No appointment details found for user id {user_id}."
    except Exception as e:
        return Chains.error_generator_chain.invoke(input={"input": f"{e}"})


# defining custom delete_data tool
@tool("delete_data", args_schema=DatabaseDeleteSchema, return_direct=True)
def delete_data(user_id):
    """This function takes one argument which is the user id and deletes data with the id. Use this tool when you need to delete any data from the database table."""
    try:
        conn, cursor = get_connection()
        search_query = f"SELECT * FROM {config["database"]["table"]} WHERE user_id = %s"
        cursor.execute(search_query, (user_id,))
        result = cursor.fetchone()   # fetch the search result
        if result:
            delete_query = f"DELETE FROM {config["database"]["table"]} WHERE user_id = %s"    # sql query for deleting data from table
            cursor.execute(delete_query, (user_id,))
            conn.commit()

            if conn.is_connected():
                cursor.close()
                conn.close()
            return f"Appointment canceled for user id {user_id}."
        else:
            if user_id.__contains__("Invalid"):
                return user_id    # it will be an error message rather than user id
            return f"No appointment details found with the user id {user_id}."
    except Exception as e:
        return Chains.error_generator_chain.invoke(input={"input": f"{e}"})


# function for generating unique user ID
def get_user_id(phone_number, sc_date, sc_time):
    return f"SC_{phone_number}_{sc_date[8:]}_{sc_time[:2]}_{sc_time[3:5]}"

