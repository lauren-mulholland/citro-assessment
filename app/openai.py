import os
import openai
from enum import Enum
from .models import Category

OPENAI_API_KEY= os.getenv("OPENAI_API_KEY")

class OpenAIModels(str, Enum):
    # prices per 1 million tokens
    #DEFAULT to lowest price model. There are other models available but noting these for now
    gpt_3_5_turbo = "gpt-3.5-turbo" #  point Input: $0.50 | Output: $1.5*
    gpt_4_turbo	 = "gpt-4-turbo" # Input: $10 | Output: $30*
    gpt_4o = "gpt-5-turbo" # Input: $5 | Output: $15*

class OpenAIUtil:
    def __init__(self, api_key:str=OPENAI_API_KEY):
        self.api_key = api_key

    def create_chat_response(self, model:OpenAIModels, query: str)->str:
        """Query the AI model with the given query and return the response as a string."""
        openapi_client = openai.OpenAI(api_key=self.api_key)
        messages=[{"role": "system", "content": query}]
        print(f"Querying AI model {model.value} with: {messages}")
        completion = openapi_client.chat.completions.create(model=model.value, messages=messages)
        return completion.choices[0].message.content

    def calc_category(self, counterpart_name:str) -> str:
        """Use the chat AI to categorize the payment based on the counterpart name.
        """
        valid_categories = [c.value for c in Category]
        chat_gpt_query = f"""Respond with the name of the category only. Categorise the payment called {counterpart_name} into one of the following categories : {valid_categories}"""
        # this is not a complex query, so we can use the gpt-3.5-turbo model
        try:
            message = self.create_chat_response(model=OpenAIModels.gpt_3_5_turbo, query=chat_gpt_query)
            if message.lower() in valid_categories:
                return message.lower()
            else:
                return "uncategorized"
        except Exception as e:
            # if the AI model fails, return uncategorized and log the error
            # TODO: in future have some error handling in general but specifically handle retries when hitting rate limits
            print(f"Error: {e}")
            return "uncategorized" 