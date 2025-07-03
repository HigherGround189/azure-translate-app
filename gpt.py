from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import os


class GPTManager():
    def __init__(self):
        load_dotenv()
        self.client = ChatCompletionsClient(
          endpoint=os.getenv('AZURE_ENDPOINT'), 
          credential=AzureKeyCredential(os.getenv('API_KEY'))
        )

        self.system_message = """
        You will be given a document, along with a question related to the paper.
        Both will be enclosed in xml tags. Here is an example:

        <document><documentFileName>Document Name</documentFileName><documentContent>Document Content</documentContent></document>
        <userquestion>What is the name of the research paper?</userquestion>

        Additionally, you will be given a chat history, in this JSON format:
        {'user':'What colour is the sky?'}, {'bot': 'It is blue!'}
        
        """

        # Uses this xml structure
        # <document>
        #     <documentFileName>{name}</documentFileName>
        #     <documentContent>{content}</documentContent>
        # </document>

    def query(self, user_query, pdf_dict, chat_history):
        pdf_xml = ""

        for name, content in pdf_dict.items():
            pdf_xml += f"<document><documentFileName>{name}</documentFileName><documentContent>{content}</documentContent></document>"

        # Convert the new chat history format to the one expected by the model
        messages = [SystemMessage(self.system_message)]
        for item in chat_history:
            role = list(item.keys())[0]
            content = list(item.values())[0]
            if role == "user":
                messages.append(UserMessage(content))
            else:
                # Assuming the bot's messages should be treated as system messages
                messages.append(SystemMessage(content))

        messages.append(UserMessage(f"""
            {pdf_xml}
            <userquestion>{user_query}</userquestion>
        """))

        response = self.client.complete(
            messages=messages,
            model="gpt-4o",
            temperature=0
        )
        
        return response.choices[0].message.content