# Schedule Management Automation using Agentic Framework

**A brief description of what this project does**

In traditional appointment booking systems, a human agent typically evaluates user requests and manages them according to specific preferences. This manual approach, while functional, often consumes significant time and resources. To address this inefficiency, this project introduces an automated solution leveraging a Large Language Model (LLM) to streamline the appointment process.

The system interacts with users in real-time, handling appointment requests and seamlessly forwarding them to the administrative team. By integrating Groq API for high-speed processing and robust database operations, the solution ensures rapid, error-free management of appointment data. Additionally, it features an interactive dashboard for easy tracking and management of appointments, reducing the need for human intervention while significantly saving time and resources.

## Table of contents
* [Features](#features)
* [Application Demo](#application-demo)
* [Installation Process](#installation-process)
* [Technologies Used](#technologies-used)


## Features
- **Insane fast response:** The agentic framework is build using Groq API which provides fast inference time with LLM.
- **Integration with WhatsApp:** This application is integrated with whatsapp which make it more user friendly.
- **Prover validation of appointment data:** The application uses <strong>Pydantic Models</strong> for creating schemas that validates the data extracted from the users query.
- **Conversational:** The AI agent can remember the previous conversations.
- **Error handling:** The agent is capable of understanding the issue and it comes up with a constructive feedback response directing the steps to resolve the issue.
- **Chat session handling:** Chat history is stored in cloud based storage.
- **Authentication system:** Multiple admin can create account and manage the appointment simultaneously.
- **Scalable admin dashboard:** The application provides a scalable dashboard for admin for efficiently managing the appointment schedules. 


## Application Demo
Here is a short video to demonstrate the application in action.

https://github.com/user-attachments/assets/e1c8a4a8-0da4-4660-98d4-719a15843900


## Installation Process
In order to run this application you just need to clone this repository, create an python environment and install the requirements.

Command for creating and activating python environment. You can use different ways to create your environment.
```python
conda create -n <env_name>
conda activate <env_name>
```

Execute the following command for installing the required libraries.
```python
pip install -r requirements.txt
```

Execute the following commands for initializing the database.
```python
python manage.py makemigrations
python manage.py migrate
```

Now, you are all set to run the application.
```python
python manage.py runserver
```

## Technologies Used
We have used several python libraries and frameworks for different purposes.

- **[Python]** - Programming language for creating whole application.
- **[LangChain, Groq API]** - These framework and API is used for creating the Agentic Framework.
- **[MySQL]** - Used for storing the appointment information.
- **[Django]** - This framework is used for handling user request in the backend. It also merges the <strong>AI Agent</strong> with the <strong>Custom SQL Tools</strong> into the application.
- **[HTML, CSS, Bootstrap, JavaScript, AJAX]** - Used for application frontend design.


## License
[MIT](LICENSE)
