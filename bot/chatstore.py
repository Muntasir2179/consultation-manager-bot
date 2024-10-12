import yaml
from google.cloud import firestore
from langchain_google_firestore import FirestoreChatMessageHistory


# loading the config file
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)


class ChatHistoryHandler:
    def __init__(self):
        self.client = firestore.Client(project=config['google-firestore']['PROJECT_ID'])
    
    # function for fetching specific chat history
    def fetch_chat_history(self, chat_session_id:str):
        return FirestoreChatMessageHistory(session_id=chat_session_id,
                                           collection=config['google-firestore']['COLLECTION_NAME'],
                                           client=self.client)
    
    # function for adding human messages to the chat history
    def add_query(self, chat_session_id, query_text):
        chat_history = self.fetch_chat_history(chat_session_id=chat_session_id)
        chat_history.add_user_message(query_text)
    
    # function for adding ai responses to the chat history
    def add_response(self, chat_session_id, response_text):
        chat_history = self.fetch_chat_history(chat_session_id=chat_session_id)
        chat_history.add_ai_message(response_text)

    # function to get the full chat history
    def get_chat_history(self, chat_session_id):
        chat_history = self.fetch_chat_history(chat_session_id=chat_session_id)
        return chat_history.messages
    
    # function to clear chat history
    def delete_chat_history(self, chat_session_id):
        chat_history = self.fetch_chat_history(chat_session_id=chat_session_id)
        chat_history.clear()

