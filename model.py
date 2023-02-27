import math
import os

import discord
import openai
from dotenv import load_dotenv


class Model:
    # TODO: implement prompt builder
    # TODO: implement logit updating
    def __init__(self):
        load_dotenv()
        openai.api_key = os.getenv('OPENAI_TOKEN')

    # TODO: make parameters changeable inside discord
    def respond(self, message_text: str) -> str:
        completion: openai.Completion = openai.Completion.create(
            model="text-davinci-003",
            prompt=message_text,
            echo=False,
            max_tokens=400,
            frequency_penalty=1,
            presence_penalty=1.5,
            temperature=0.75)

        response = completion['choices'][0]['text']

        return response

    # TODO: implement historical db for users
    def build_prompt(self, seed: discord.message, recent_history: list[discord.message]):
        pass


# makes a conservative estimate of the number of tokens in text following rules at:
# https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them
def estimate_tokens(text: str):
    tokens_by_character = math.ceil(len(text)/4.0)
    tokens_by_word = math.ceil(len(text.split(' '))*0.75)

    return max(tokens_by_character, tokens_by_word)
