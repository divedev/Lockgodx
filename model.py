import os

import openai
from dotenv import load_dotenv


class Model:  # TODO: implement base prompt building, saving, and swapping
    def __init__(self):
        load_dotenv()
        openai.api_key = os.getenv('OPENAI_TOKEN')

    # TODO: make parameters changeable inside discord
    def respond(self, message_text: str) -> str:
        completion = openai.Completion.create(
            model="text-davinci-003",
            prompt=message_text,
            echo=False,
            max_tokens=400,
            frequency_penalty=1,
            presence_penalty=1.5,
            temperature=0.75)

        response = completion['choices'][0]['text']

        return response
