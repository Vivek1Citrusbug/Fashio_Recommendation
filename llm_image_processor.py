import logging
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPEN_AI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")

llm_client = OpenAI(api_key=OPENAI_API_KEY)

logging.basicConfig(level=logging.ERROR)

def capture_exception(e):
    logging.error("An error occurred: %s", e)

# ======================================================================================================
system_prompt = """
You are FASHION recommender bot, You are provided with metadata of clothing items and you have to create best outfit from them.
"""

user_prompt = """
## Clothing Items : 
```
items_list
```
"""
# ======================================================================================================

class LLMImageProcessor:
    def __init__(self, client):
        self.client = client

    def _get_message_list(self, system_prompt: str, user_prompt: str, prompt_variables: dict = {}, image_url: str = None) -> list:
        """
        Retrieves a list of messages based on the provided prompt type, variables, and optional image URL.

        Parameters:
            prompt_type (str): The type of prompt to retrieve messages for.
            prompt_variables (dict, optional): Variables to replace in the user prompt. Defaults to {}.
            image_url (str, optional): The URL of the image to include in the message. Defaults to None.

        Returns:
            list: A list of dictionaries containing system and user messages based on the input parameters.
        """
        try:
            for key, value in prompt_variables.items():
                user_prompt = user_prompt.replace(key, value)

            if not image_url:
                return [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ]
            else:
                return [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url, "detail": "high"},
                            },
                        ],
                    },
                ]
        except Exception as e:
            capture_exception(e)

    def generate(self, system_prompt: str, user_prompt: str, prompt_variables: dict = {}, model_data_dict: dict = None, image_url: str = None):
        """
        Generates a chat completion based on the provided prompt type, variables, model data, and image URL.

        Parameters:
            prompt_type (str): The type of prompt to generate messages for.
            prompt_variables (dict, optional): Variables to replace in the user prompt. Defaults to {}.
            model_data_dict (dict, optional): Model data dictionary for customizing the LLM model. Defaults to None.
            image_url (str, optional): The URL of the image to include in the message. Defaults to None.

        Returns:
            dict: The completion response from the chat generation process.
        """
        try:
            messages = self._get_message_list(
                system_prompt = system_prompt,
                user_prompt=user_prompt,
                prompt_variables=prompt_variables,
                image_url=image_url,
            )
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                # response_format={"type": "json_object"},
                temperature=0.1,
            )
            return response
        except Exception as e:
            capture_exception(e)

def main():
    image_processor = LLMImageProcessor(client=llm_client)
    prompt_variables = {"items_list": "A stylish red dress"} 
    image_url = "https://i.imgur.com/eAfpeBY.jpeg"
    response = image_processor.generate(system_prompt, user_prompt, prompt_variables, image_url=image_url)
    print("Response from Openai = ",response)

if __name__ == "__main__":
    main()
