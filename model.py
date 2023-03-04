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

        self.name: str = "idiot"
        self.traits: list[str] = []  # TODO: get from bot

    # TODO: make parameters changeable inside discord
    def get_openai_response(self, seed: discord.Message, recent_history: list[discord.Message]) -> str:
        completion: openai.Completion = openai.Completion.create(
            model="text-davinci-003",
            prompt=self.build_prompt(seed=seed.content, recent_history=recent_history),
            echo=False,
            max_tokens=400,
            frequency_penalty=1,
            presence_penalty=1.5,
            temperature=0.75)

        response = completion['choices'][0]['text']

        return response

    # TODO: implement historical db for users
    def build_prompt(self, seed: str, recent_history: list[discord.Message]) -> str:
        history_formatted = format_recent_history(recent_history)
        prompt_template = f"{self.name} is a participant in a natural conversation with other people." \
                          f"{self.name} makes low quality shitposts based on recent conversation history. These shitposts have a " \
                          f"personality given by a list of traits that describe {self.name}, but {self.name} never " \
                          f"discusses these traits or mentions them at all. {self.name}'s responses are made directly to a specific seed " \
                          f"prompt, but also reference the context of recent history." \
                          f"Traits:{format_traits(self.traits)}" \
                          f"\nRecent history: {history_formatted}" \
                          f"\nSeed Prompt:{seed}" \
                          f"\n{self.name}:"
        return prompt_template


# TODO: we dont need to keep a list at all. probably should just keep self.traits as one string
def format_traits(traits: list[str]):
    return " ".join(f"{trait}, " for trait in traits)[:-2]


def format_recent_history(recent_history: list[discord.Message]):
    l = [f"{msg.author.name} said \"{msg.content}\"" for msg in recent_history]
    ret: str = " ".join(l)

    return ret


# makes a conservative estimate of the number of tokens in text following rules at:
# https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them
def estimate_tokens(text: str) -> int:
    tokens_by_character = math.ceil(len(text) / 4.0)
    tokens_by_word = math.ceil(len(text.split(' ')) * 0.75)

    return max(tokens_by_character, tokens_by_word)
